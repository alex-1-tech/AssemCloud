"""URL configuration for the core application."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from core import views

urlpatterns = [
    path(
        "admin/api/get-schemes/",
        views.get_schemes_for_model,
        name="get_schemes_for_model"
    ),
    path(
        "api/<str:model_name>/",
        views.EquipmentCreateView.as_view(),
        name="create",
    ),
    path(
        "api/<str:model_name>/<str:serial_number>/get_settings",
        views.EquipmentRetrieveView.as_view(),
        name="get-settings",
    ),
]

urlpatterns += [
    # App file management
    path("apps/upload/", views.AppUploadPageView.as_view(), name="app-upload-page"),
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
    path(
        "api/apps/last_version/<str:app_type>/",
        views.AppFileLatestVersionDateView.as_view(),
        name="app-versions",
    ),
    # license
    path(
        "api/activate/<str:serial_number>/",
        views.ActivateView.as_view(),
        name="activate-license",
    ),
    # auth
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="admin/login.html", next_page="/apps/upload/"),
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/apps/upload/"), name="logout"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
