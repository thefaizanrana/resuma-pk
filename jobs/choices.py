"""Shared enums and canonical lists for Resuma.pk."""

from django.db import models


class JobType(models.TextChoices):
    FULL_TIME = "full_time", "Full-time"
    PART_TIME = "part_time", "Part-time"
    REMOTE = "remote", "Remote"
    CONTRACT = "contract", "Contract"
    INTERNSHIP = "internship", "Internship"


class ExperienceLevel(models.TextChoices):
    FRESH = "fresh", "Fresh Graduate"
    JUNIOR = "junior", "Entry Level (1-2 yrs)"
    MID = "mid", "Mid Level (3-5 yrs)"
    SENIOR = "senior", "Senior Level (5+ yrs)"
    LEAD = "lead", "Manager / Lead"


class SalaryPeriod(models.TextChoices):
    MONTHLY = "monthly", "per month"
    ANNUAL = "annual", "per year"
    HOURLY = "hourly", "per hour"


class ApplyMethod(models.TextChoices):
    EMAIL = "email", "Apply by email"
    URL = "url", "Apply on website"


class JobStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    CLOSED = "closed", "Closed"


class ApplicationStatus(models.TextChoices):
    RECEIVED = "received", "Received"
    REVIEWING = "reviewing", "Under Review"
    SHORTLISTED = "shortlisted", "Shortlisted"
    REJECTED = "rejected", "Rejected"
    HIRED = "hired", "Hired"


# Major Pakistani cities (common, Rozee/Mustakbil style)
CITIES = [
    "Karachi",
    "Lahore",
    "Islamabad",
    "Rawalpindi",
    "Faisalabad",
    "Multan",
    "Peshawar",
    "Quetta",
    "Gujranwala",
    "Sialkot",
    "Hyderabad",
    "Sargodha",
    "Bahawalpur",
    "Abbottabad",
    "Murree",
    "Gujrat",
    "Jhelum",
    "Sahiwal",
    "Gawadar",
    "Remote / Anywhere",
]

CITY_CHOICES = [(city, city) for city in CITIES]

# Industries used across Pakistani job portals
INDUSTRIES = [
    "Information Technology",
    "Banking / Financial Services",
    "Education / Training",
    "Healthcare / Medical",
    "Sales & Business Development",
    "Marketing & Advertising",
    "Manufacturing",
    "E-Commerce",
    "Telecommunications",
    "Real Estate / Property",
    "Call Center / BPO",
    "NGO / Social Services",
    "Travel / Tourism",
    "Logistics / Supply Chain",
    "Retail",
    "Construction / Engineering",
    "Textiles / Fashion",
    "Food & Beverage",
]

INDUSTRY_CHOICES = [(ind, ind) for ind in INDUSTRIES]

# Functional areas / job categories
JOB_CATEGORIES = [
    ("software", "Software & Web Development"),
    ("design", "Creative Design"),
    ("marketing", "Marketing & Communications"),
    ("sales", "Sales & BD"),
    ("accounts", "Accounts & Finance"),
    ("hr", "Human Resources"),
    ("admin", "Administration"),
    ("customer", "Customer Service"),
    ("teaching", "Teaching & Education"),
    ("health", "Health & Medicine"),
    ("engineering", "Engineering"),
    ("operations", "Operations / Management"),
    ("writing", "Writing & Content"),
    ("logistics", "Logistics & Distribution"),
    ("other", "Other"),
]

CATEGORY_CHOICES = JOB_CATEGORIES