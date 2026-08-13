from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from jobs.choices import INDUSTRY_CHOICES
from jobs.forms import CompanyForm
from jobs.models import Company

from .forms import (
    EmployerRegistrationForm,
    JobSeekerProfileForm,
    LoginForm,
    SeekerRegistrationForm,
)
from .models import JobSeekerProfile


def register_seeker(request):
    if request.user.is_authenticated:
        return redirect("jobs:home")
    form = SeekerRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome to Resuma.pk, {user.first_name}!")
        return redirect("accounts:seeker_dashboard")
    return render(
        request,
        "accounts/register.html",
        {"form": form, "role": "seeker", "industries": INDUSTRY_CHOICES},
    )


def register_employer(request):
    if request.user.is_authenticated:
        return redirect("jobs:home")
    form = EmployerRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        company = Company.objects.create(
            owner=user,
            name=form.cleaned_data["company_name"],
            industry=form.cleaned_data.get("industry") or "",
        )
        login(request, user)
        messages.success(request, "Company account created. Complete your company profile.")
        return redirect("accounts:company_setup")
    return render(
        request,
        "accounts/register.html",
        {"form": form, "role": "employer", "industries": INDUSTRY_CHOICES},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("jobs:home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get("next")
        return redirect(next_url or "jobs:home")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("jobs:home")


@login_required
def profile(request):
    if request.user.is_employer:
        company = getattr(request.user, "managed_company", None)
        form = CompanyForm(request.POST or None, request.FILES or None, instance=company) if company else CompanyForm(request.POST or None, request.FILES or None)
        template = "accounts/company_form.html"
        if request.method == "POST" and form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()
            messages.success(request, "Company profile saved.")
            return redirect("accounts:employer_dashboard")
        return render(request, template, {"form": form, "company": company})

    profile_obj, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
    form = JobSeekerProfileForm(request.POST or None, request.FILES or None, instance=profile_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:seeker_dashboard")
    return render(request, "accounts/seeker_profile.html", {"form": form})


@login_required
def company_setup(request):
    company = getattr(request.user, "managed_company", None)
    form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
    if request.method == "POST" and form.is_valid():
        company = form.save(commit=False)
        company.owner = request.user
        company.save()
        messages.success(request, "Company profile saved. You can now post jobs.")
        return redirect("accounts:employer_dashboard")
    return render(
        request,
        "accounts/company_form.html",
        {"form": form, "company": company, "industries": INDUSTRY_CHOICES},
    )