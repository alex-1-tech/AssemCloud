"""URL configuration for the core application."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from core import views

# MachineDuplicateView,
# MachinePDFView,
urlpatterns = [
    path("machines/", views.MachineListView.as_view(), name="machine_list"),
    path("machines/add/", views.MachineCreateView.as_view(), name="machine_add"),
    path(
        "machines/<int:pk>/edit/",
        views.MachineUpdateView.as_view(),
        name="machines_edit",
    ),
    path(
        "machines/<int:pk>/",
        views.MachineDetailView.as_view(),
        name="machines_detail",
    ),
    path(
        "machines/<int:pk>/delete/",
        views.MachineDeleteView.as_view(),
        name="machines_delete",
    ),
]
urlpatterns += [
    path(
        "api/kalmar32/",
        views.Kalmar32CreateView.as_view(),
        name="kalmar32-create",
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
