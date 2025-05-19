"""URL configuration for the assembler project."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("select2/", include("django_select2.urls")),
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
]
