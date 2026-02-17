"""Views package exports for core application."""

from core.views.appfile import (
    AppFileDownloadView,
    AppFileLatestVersionDateView,
    AppFileListVersionsView,
    AppFileUploadView,
    AppUploadPageView,
)
from core.views.create_model import EquipmentCreateView
from core.views.kalmar32 import (
    Kalmar32GetReportsView,
    Kalmar32RetrieveView,
)
from core.views.license import ActivateView
from core.views.phasar32 import (
    Phasar32GetReportsView,
    Phasar32RetrieveView,
)
from core.views.report import ReportCreateView, ReportFileUploadView
from core.views.webhook import AppWebhookDownloadView

__all__ = [
    "ActivateView",
    "AppFileDownloadView",
    "AppFileLatestVersionDateView",
    "AppFileListVersionsView",
    "AppFileUploadView",
    "AppUploadPageView",
    "AppWebhookDownloadView",
    "EquipmentCreateView",
    "Kalmar32GetReportsView",
    "Kalmar32RetrieveView",
    "Phasar32GetReportsView",
    "Phasar32RetrieveView",
    "ReportCreateView",
    "ReportFileUploadView",
]
