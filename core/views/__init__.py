"""Views package exports for core application."""

from core.views.admin_views import get_schemes_for_model
from core.views.appfile import (
    AppFileDownloadView,
    AppFileLatestVersionDateView,
    AppFileListVersionsView,
    AppFileUploadView,
    AppUploadPageView,
)
from core.views.create_model import EquipmentCreateView
from core.views.license import ActivateView
from core.views.models import EquipmentRetrieveView
from core.views.schemes import AllSchemesExportView
from core.views.versions import AllVersionsView

__all__ = [
    "ActivateView",
    "AllSchemesExportView",
    "AllVersionsView",
    "AppFileDownloadView",
    "AppFileLatestVersionDateView",
    "AppFileListVersionsView",
    "AppFileUploadView",
    "AppUploadPageView",
    "EquipmentCreateView",
    "EquipmentRetrieveView",
    "get_schemes_for_model"
]
