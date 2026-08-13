from django.contrib import admin
from django.utils.html import format_html

from .models import Application, Company, Job, SavedJob


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "city", "verified", "owner")
    list_filter = ("verified", "industry", "city")
    search_fields = ("name", "tagline")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "city", "job_type", "status", "is_featured", "posted_at")
    list_filter = ("status", "job_type", "is_featured", "city", "category")
    search_fields = ("title", "company__name", "skills")
    prepopulated_fields = {"slug": ("title",)}
    actions = ["make_active", "make_featured"]

    @admin.action(description="Mark selected jobs as active")
    def make_active(self, request, queryset):
        queryset.update(status="active")

    @admin.action(description="Feature selected jobs")
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "email", "status", "applied_at")
    list_filter = ("status", "applied_at")
    search_fields = ("job__title", "applicant__email", "email")


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "saved_at")
    search_fields = ("user__email", "job__title")