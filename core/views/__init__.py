"""Views package exports for core application."""

from core.views.appfile import (
    AppFileDownloadView,
    AppFileListVersionsView,
    AppFileUploadView,
    AppUploadPageView,
)
from core.views.kalmar32 import (
    Kalmar32CreateView,
    Kalmar32GetReportsView,
    Kalmar32RetrieveView,
)
from core.views.phasar32 import (
    Phasar32CreateView,
    Phasar32GetReportsView,
    Phasar32RetrieveView,
)
from core.views.report import ReportCreateView, ReportFileUploadView

__all__ = [
    "AppFileDownloadView",
    "AppFileListVersionsView",
    "AppFileUploadView",
    "AppUploadPageView",
    "Kalmar32CreateView",
    "Kalmar32GetReportsView",
    "Kalmar32RetrieveView",
    "Phasar32CreateView",
    "Phasar32GetReportsView",
    "Phasar32RetrieveView",
    "ReportCreateView",
    "ReportFileUploadView",
]
