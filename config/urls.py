from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from jobs import views as jobs_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("jobs.urls")),
    path("", include("accounts.urls")),
]

handler404 = "jobs.views.handlers_404"
handler500 = "jobs.views.handlers_500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)