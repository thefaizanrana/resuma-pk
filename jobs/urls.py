from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.home, name="home"),
    path("jobs/", views.job_list, name="job_list"),
    path("categories/", views.categories, name="categories"),
    path("alerts/subscribe/", views.job_alert, name="job_alert"),
    path("job/<slug:slug>/", views.job_detail, name="job_detail"),
    path("job/<slug:slug>/apply/", views.apply_job, name="apply_job"),
    path("job/<slug:slug>/save/", views.save_job, name="save_job"),
    path("companies/", views.company_list, name="company_list"),
    path("company/<slug:slug>/", views.company_detail, name="company_detail"),
    # Static pages
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("faq/", views.faq, name="faq"),
]