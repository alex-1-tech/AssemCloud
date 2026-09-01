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

__all__ = [
    "ActivateView",
    "AppFileDownloadView",
    "AppFileLatestVersionDateView",
    "AppFileListVersionsView",
    "AppFileUploadView",
    "AppUploadPageView",
    "EquipmentCreateView",
    "EquipmentRetrieveView",
    "get_schemes_for_model",
]
