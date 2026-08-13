from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .choices import (
    ApplyMethod,
    ApplicationStatus,
    CATEGORY_CHOICES,
    CITY_CHOICES,
    ExperienceLevel,
    INDUSTRY_CHOICES,
    JobStatus,
    JobType,
    SalaryPeriod,
)


class Company(models.Model):
    """A company with a public profile page."""

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_company",
        help_text="Employer account that manages this company.",
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    logo = models.ImageField(upload_to="companies/logos/", blank=True, null=True)
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=80, choices=INDUSTRY_CHOICES, blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=60, blank=True)
    address = models.CharField(max_length=255, blank=True)
    founded = models.PositiveSmallIntegerField(null=True, blank=True)
    employees = models.CharField(max_length=30, blank=True, help_text="e.g. 51-200")
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Company.objects.filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("jobs:company_detail", kwargs={"slug": self.slug})

    @property
    def active_jobs(self):
        return self.jobs.filter(status=JobStatus.ACTIVE)


class JobQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=JobStatus.ACTIVE)

    def featured(self):
        return self.active().filter(is_featured=True)


class Job(models.Model):
    """A single job posting."""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="jobs"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="other")
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    experience_level = models.CharField(
        max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.FRESH
    )
    city = models.CharField(max_length=60, choices=CITY_CHOICES)
    is_remote = models.BooleanField(default=False)

    salary_min = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    salary_max = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    salary_period = models.CharField(
        max_length=10, choices=SalaryPeriod.choices, default=SalaryPeriod.MONTHLY
    )

    description = models.TextField(help_text="What the job involves.")
    responsibilities = models.TextField(blank=True, help_text="One bullet point per line.")
    requirements = models.TextField(blank=True, help_text="One bullet point per line.")
    skills = models.CharField(max_length=300, blank=True, help_text="Comma-separated skills.")

    apply_method = models.CharField(max_length=10, choices=ApplyMethod.choices, default=ApplyMethod.EMAIL)
    apply_email = models.EmailField(blank=True)
    apply_url = models.URLField(blank=True)

    status = models.CharField(max_length=10, choices=JobStatus.choices, default=JobStatus.DRAFT)
    is_featured = models.BooleanField(default=False)
    deadline = models.DateField(null=True, blank=True)

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    views = models.PositiveIntegerField(default=0)
    posted_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["status", "posted_at"]),
            models.Index(fields=["city"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug, n = base, 1
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("jobs:job_detail", kwargs={"slug": self.slug})

    @property
    def salary_display(self):
        if not self.salary_min and not self.salary_max:
            return "Not disclosed"
        low = f"{self.salary_min:,}" if self.salary_min else "—"
        high = f"{self.salary_max:,}" if self.salary_max else "—"
        return f"Rs. {low} - Rs. {high} {self.get_salary_period_display()}"

    @property
    def location_display(self):
        return "Remote" if self.is_remote and self.city == "Remote / Anywhere" else self.city

    @property
    def is_expired(self):
        return bool(self.deadline and self.deadline < timezone.localdate())


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "job")

    def __str__(self):
        return f"{self.user} saved {self.job}"


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to="applications/resumes/", blank=True)
    status = models.CharField(
        max_length=15, choices=ApplicationStatus.choices, default=ApplicationStatus.RECEIVED
    )
    note = models.CharField(max_length=255, blank=True, help_text="Private note for the employer.")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "applicant")
        ordering = ["-applied_at"]

    STATUS_CHOICES = ApplicationStatus.choices

    def __str__(self):
        return f"{self.applicant} -> {self.job}"