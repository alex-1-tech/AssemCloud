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


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
