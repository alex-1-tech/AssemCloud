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
        "api/phasar32/",
        views.Phasar32CreateView.as_view(),
        name="phasar32-create",
    ),
    path(
        "api/phasar32/<str:pk>/get_settings",
        views.Phasar32RetrieveView.as_view(),
        name="phasar32-get-settings",
    ),
    path(
        "api/phasar32/<str:pk>/get_reports",
        views.Phasar32GetReportsView.as_view(),
        name="phasar32-get-reports",
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

urlpatterns += [
    # App file management
    path("api/apps/upload/", views.AppFileUploadView.as_view(), name="app-upload"),
    path(
        "api/apps/download/<str:app_type>/",
        views.AppFileDownloadView.as_view(),
        name="app-download",
    ),
    path(
        "api/apps/versions/<str:app_type>/",
        views.AppFileListVersionsView.as_view(),
        name="app-versions",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
