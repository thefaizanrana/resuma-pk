from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = "seeker", "Job Seeker"
        EMPLOYER = "employer", "Employer"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.JOB_SEEKER)
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER

    @property
    def is_seeker(self):
        return self.role == self.Role.JOB_SEEKER


class JobSeekerProfile(models.Model):
    """Profile for a job seeker (resume, city, skills)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seeker_profile")
    city = models.CharField(max_length=60, blank=True)
    title = models.CharField(max_length=150, blank=True, help_text="e.g. Django Developer")
    summary = models.TextField(blank=True)
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated")
    resume = models.FileField(upload_to="seekers/resumes/", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s profile"