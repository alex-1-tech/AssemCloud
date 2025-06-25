"""URL configuration for the assembler project."""

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("select2/", include("django_select2.urls")),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]


urlpatterns += [
    re_path(
        r"^.well-known/appspecific/com.chrome.devtools.json$",
        serve,
        {
            "document_root": (
                "/home/alex/projects/AssemCloud/assembler/.well-known/appspecific"
            ),
            "path": "com.chrome.devtools.json",
        },
    ),
]
