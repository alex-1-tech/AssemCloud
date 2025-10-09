"""URL configuration for the core application."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from core import views

urlpatterns = [
    path(
        "api/kalmar32/",
        views.Kalmar32CreateView.as_view(),
        name="kalmar32-create",
    ),
    path(
        "api/kalmar32/<str:pk>/get_settings",
        views.Kalmar32RetrieveView.as_view(),
        name="kalmar32-get-settings",
    ),
    path(
        "api/kalmar32/<str:pk>/get_reports",
        views.Kalmar32GetReportsView.as_view(),
        name="kalmar32-get-reports",
    ),
    path(
        "api/report/",
        views.ReportCreateView.as_view(),
        name="report-create",
    ),
    path(
        "api/report/<str:report_identifier>/<str:file_type>/",
        views.ReportFileUploadView.as_view(),
        name="report-upload-file",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
