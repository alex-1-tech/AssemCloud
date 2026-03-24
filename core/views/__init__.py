"""Views package exports for core application."""

from core.views.appfile import (
    AppFileDownloadView,
    AppFileLatestVersionDateView,
    AppFileListVersionsView,
    AppFileUploadView,
    AppUploadPageView,
)
from core.views.create_model import EquipmentCreateView
from core.views.license import ActivateView
from core.views.models import EquipmentReportsView, EquipmentRetrieveView
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
    "EquipmentReportsView",
    "EquipmentRetrieveView",
    "ReportCreateView",
    "ReportFileUploadView",
]
