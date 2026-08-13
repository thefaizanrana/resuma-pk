"""Views for the Resuma.pk jobs app."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .choices import ApplyMethod, JobStatus
from .forms import ApplicationForm, CompanyForm, JobForm, SearchForm
from .models import Application, Company, Job, SavedJob

JOBS_PER_PAGE = 12


def home(request):
    featured = Job.objects.featured().select_related("company")[:8]
    latest = Job.objects.active().select_related("company")[:8]
    companies = (
        Company.objects.annotate(job_count=Count("jobs", filter=Q(jobs__status=JobStatus.ACTIVE)))
        .filter(job_count__gt=0)
        .order_by("-job_count")[:8]
    )
    categories = (
        Job.objects.active()
        .values("category")
        .annotate(count=Count("id"))
        .order_by("-count")[:8]
    )
    cities = (
        Job.objects.active()
        .values("city")
        .annotate(count=Count("id"))
        .order_by("-count")[:6]
    )
    total_jobs = Job.objects.active().count()
    return render(
        request,
        "jobs/home.html",
        {
            "featured_jobs": featured,
            "latest_jobs": latest,
            "companies": companies,
            "categories": categories,
            "cities": cities,
            "total_jobs": total_jobs,
            "search_form": SearchForm(request.GET),
        },
    )


def job_list(request):
    form = SearchForm(request.GET)
    jobs = Job.objects.active().select_related("company")

    if form.is_valid():
        q = form.cleaned_data["q"]
        city = form.cleaned_data["city"]
        job_type = form.cleaned_data["job_type"]
        experience = form.cleaned_data["experience"]
        category = form.cleaned_data["category"]

        if q:
            jobs = jobs.filter(
                Q(title__icontains=q)
                | Q(company__name__icontains=q)
                | Q(skills__icontains=q)
                | Q(description__icontains=q)
            )
        if city:
            jobs = jobs.filter(city=city)
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        if experience:
            jobs = jobs.filter(experience_level=experience)
        if category:
            jobs = jobs.filter(category=category)

    sort = request.GET.get("sort", "newest")
    if sort == "salary":
        jobs = jobs.order_by("-salary_max", "-posted_at")
    elif sort == "oldest":
        jobs = jobs.order_by("posted_at")
    else:
        jobs = jobs.order_by("-posted_at")

    paginator = Paginator(jobs, JOBS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    qs_params = request.GET.copy()
    qs_params.pop("page", None)
    querystring = qs_params.urlencode() + ("&" if qs_params else "")

    return render(
        request,
        "jobs/job_list.html",
        {
            "page_obj": page_obj,
            "form": form,
            "sort": sort,
            "total": paginator.count,
            "querystring": querystring,
        },
    )


def job_detail(request, slug):
    job = get_object_or_404(
        Job.objects.select_related("company"), slug=slug, status=JobStatus.ACTIVE
    )
    if job.views is None:
        job.views = 0
    Job.objects.filter(pk=job.pk).update(views=job.views + 1)

    related = (
        Job.objects.active()
        .filter(Q(category=job.category) | Q(company=job.company))
        .exclude(pk=job.pk)
        .select_related("company")[:4]
    )

    saved = False
    has_applied = False
    if request.user.is_authenticated:
        saved = SavedJob.objects.filter(user=request.user, job=job).exists()
        has_applied = Application.objects.filter(applicant=request.user, job=job).exists()

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job,
            "related_jobs": related,
            "is_saved": saved,
            "has_applied": has_applied,
            "apply_form": ApplicationForm(user=request.user if request.user.is_authenticated else None),
        },
    )


@require_POST
@login_required
def apply_job(request, slug):
    job = get_object_or_404(Job, slug=slug, status=JobStatus.ACTIVE)
    if Application.objects.filter(applicant=request.user, job=job).exists():
        messages.info(request, "You have already applied to this job.")
        return redirect("jobs:job_detail", slug=job.slug)

    form = ApplicationForm(request.POST, request.FILES, user=request.user)
    if form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.applicant = request.user
        application.save()

        send_mail(
            f"New application for {job.title} at {job.company.name}",
            f"{request.user.get_full_name()} ({application.email}) applied via Resuma.pk.\n"
            f"Phone: {application.phone or 'n/a'}\n"
            f"Cover letter:\n{application.cover_letter}",
            None,
            [job.company.email or job.apply_email or "hello@resuma.pk"],
            fail_silently=True,
        )

        messages.success(request, "Application submitted. Best of luck!")
        return redirect("jobs:job_detail", slug=job.slug)

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job,
            "related_jobs": Job.objects.active().filter(category=job.category).exclude(pk=job.pk)[:4],
            "is_saved": SavedJob.objects.filter(user=request.user, job=job).exists(),
            "has_applied": False,
            "apply_form": form,
        },
        status=422,
    )


@require_POST
@login_required
def save_job(request, slug):
    job = get_object_or_404(Job, slug=slug, status=JobStatus.ACTIVE)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()
    return JsonResponse({"saved": created})


def company_list(request):
    companies = (
        Company.objects.annotate(job_count=Count("jobs", filter=Q(jobs__status=JobStatus.ACTIVE)))
        .order_by("-job_count", "name")
    )
    paginator = Paginator(companies, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "jobs/company_list.html",
        {"page_obj": page_obj, "total": paginator.count, "querystring": ""},
    )


def company_detail(request, slug):
    company = get_object_or_404(
        Company.objects.annotate(job_count=Count("jobs", filter=Q(jobs__status=JobStatus.ACTIVE))),
        slug=slug,
    )
    jobs = company.jobs.active().select_related("company")
    return render(request, "jobs/company_detail.html", {"company": company, "jobs": jobs})


# ---------------------------------------------------------------------------
# Employer dashboard
# ---------------------------------------------------------------------------
@login_required
def employer_dashboard(request):
    if not request.user.is_employer:
        return redirect("accounts:register_employer")
    company = getattr(request.user, "managed_company", None)
    jobs = Job.objects.filter(company=company).annotate(
        applicants=Count("applications")
    ) if company else Job.objects.none()
    applications = (
        Application.objects.filter(job__company=company)
        .select_related("job", "applicant")
        .order_by("-applied_at")
    ) if company else Application.objects.none()
    return render(
        request,
        "accounts/employer_dashboard.html",
        {
            "company": company,
            "jobs": jobs,
            "applications": applications,
            "active_jobs": jobs.filter(status=JobStatus.ACTIVE).count(),
            "total_applications": applications.count(),
        },
    )


@login_required
def job_create(request):
    company = getattr(request.user, "managed_company", None)
    if not company:
        messages.warning(request, "Create your company profile before posting a job.")
        return redirect("accounts:company_setup")
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.posted_by = request.user
            job.status = JobStatus.ACTIVE
            job.save()
            messages.success(request, "Job published.")
            return redirect("accounts:employer_dashboard")
    else:
        form = JobForm()
    return render(request, "accounts/job_form.html", {"form": form, "company": company, "edit": False})


@login_required
def job_update(request, slug):
    job = get_object_or_404(Job, slug=slug, company__owner=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated.")
            return redirect("accounts:employer_dashboard")
    else:
        form = JobForm(instance=job)
    return render(request, "accounts/job_form.html", {"form": form, "company": job.company, "edit": True})


@require_POST
@login_required
def job_toggle_status(request, slug):
    job = get_object_or_404(Job, slug=slug, company__owner=request.user)
    job.status = JobStatus.CLOSED if job.status == JobStatus.ACTIVE else JobStatus.ACTIVE
    job.save(update_fields=["status", "updated_at"])
    return JsonResponse({"status": job.status})


@require_POST
@login_required
def job_delete(request, slug):
    job = get_object_or_404(Job, slug=slug, company__owner=request.user)
    job.delete()
    messages.success(request, "Job deleted.")
    return redirect("accounts:employer_dashboard")


@login_required
def job_applicants(request, slug):
    job = get_object_or_404(Job, slug=slug, company__owner=request.user)
    applications = job.applications.select_related("applicant").order_by("-applied_at")
    return render(
        request, "accounts/applicants.html", {"job": job, "applications": applications}
    )


@require_POST
@login_required
def application_status(request, pk):
    application = get_object_or_404(
        Application, pk=pk, job__company__owner=request.user
    )
    status = request.POST.get("status", "")
    allowed = {"received", "reviewing", "shortlisted", "rejected", "hired"}
    if status not in allowed:
        return HttpResponseBadRequest("Invalid status")
    application.status = status
    application.save(update_fields=["status"])
    return JsonResponse({"status": application.status})


# ---------------------------------------------------------------------------
# Job seeker dashboard
# ---------------------------------------------------------------------------
@login_required
def seeker_dashboard(request):
    if not request.user.is_seeker:
        return redirect("accounts:login")
    saved = SavedJob.objects.filter(user=request.user).select_related("job__company").order_by("-saved_at")
    applications = (
        Application.objects.filter(applicant=request.user)
        .select_related("job__company")
        .order_by("-applied_at")
    )
    profile = getattr(request.user, "seeker_profile", None)
    return render(
        request,
        "accounts/seeker_dashboard.html",
        {"saved_jobs": saved, "applications": applications, "profile": profile},
    )


# ---------------------------------------------------------------------------
# Static pages
# ---------------------------------------------------------------------------
def about(request):
    return render(request, "pages/about.html")


def contact(request):
    sent = False
    if request.method == "POST":
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        subject = request.POST.get("subject", "")
        message = request.POST.get("message", "")
        if name and email and message:
            send_mail(
                f"[Resuma.pk] {subject or 'Contact form'}",
                f"From: {name} <{email}>\n\n{message}",
                None,
                ["hello@resuma.pk"],
                fail_silently=True,
            )
            sent = True
    return render(request, "pages/contact.html", {"sent": sent})


def privacy(request):
    return render(request, "pages/privacy.html")


def terms(request):
    return render(request, "pages/terms.html")


def faq(request):
    faqs = [
        (
            "Is Resuma.pk really free for job seekers?",
            "Yes — completely. Creating a profile, uploading your resume, saving jobs and applying are free forever. "
            "We never sell your data and you'll never hit a paywall as a candidate.",
        ),
        (
            "How do I apply for a job?",
            "Open any job listing and tap the “Apply now” button. Sign in (or create a free account), review your "
            "details, and submit. Your application goes straight to the employer and appears in your dashboard "
            "with its status.",
        ),
        (
            "Which cities does Resuma cover?",
            "All of Pakistan. Job listings are tagged to specific cities — Karachi, Lahore, Islamabad, Rawalpindi, "
            "Faisalabad, Multan, Peshawar, Quetta and many more — plus a fully remote category.",
        ),
        (
            "What does it cost to post a job?",
            "Posting jobs is free during Resuma's early days. Employers get a dashboard to manage listings and "
            "review applicants. Premium features like featured placement may be added later.",
        ),
        (
            "How do employers receive applications?",
            "Applications land in the employer dashboard the moment a candidate applies, and we email a copy to "
            "the company's contact address. Employers can shortlist, review or reject candidates with one click.",
        ),
        (
            "How do I update or delete my job posting?",
            "Sign in to your employer dashboard, find the job and use the Edit, Close or Delete actions. Closing "
            "a job keeps it hidden from search while preserving your application history.",
        ),
        (
            "Is my resume visible to everyone?",
            "No. Your resume is only shared with the company you apply to. We never publish it publicly or sell it.",
        ),
        (
            "How do I report a suspicious job posting?",
            "Use the contact form or email us at hello@resuma.pk with the job link. We review every report and "
            "remove fraudulent postings quickly.",
        ),
    ]
    return render(request, "pages/faq.html", {"faqs": faqs})


def handlers_404(request, exception):
    return render(request, "pages/404.html", status=404)


def handlers_500(request):
    return render(request, "pages/500.html", status=500)