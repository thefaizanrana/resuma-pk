from django.urls import path

from jobs import views as jobs_views

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_seeker, name="register"),
    path("register/employer/", views.register_employer, name="register_employer"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("employer/company/", views.company_setup, name="company_setup"),
    path("dashboard/", jobs_views.seeker_dashboard, name="seeker_dashboard"),
    path("dashboard/employer/", jobs_views.employer_dashboard, name="employer_dashboard"),
    path("dashboard/employer/job/new/", jobs_views.job_create, name="job_create"),
    path("dashboard/employer/job/<slug:slug>/edit/", jobs_views.job_update, name="job_update"),
    path("dashboard/employer/job/<slug:slug>/toggle/", jobs_views.job_toggle_status, name="job_toggle_status"),
    path("dashboard/employer/job/<slug:slug>/delete/", jobs_views.job_delete, name="job_delete"),
    path("dashboard/employer/job/<slug:slug>/applicants/", jobs_views.job_applicants, name="job_applicants"),
    path("application/<int:pk>/status/", jobs_views.application_status, name="application_status"),
]