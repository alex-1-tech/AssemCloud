"""Views package exports for core application."""

from core.views.kalmar32 import Kalmar32CreateView
from core.views.machine import (
    MachineCreateView,
    MachineDeleteView,
    MachineDetailView,
    MachineDuplicateView,
    MachineListView,
    MachinePDFView,
    MachineUpdateView,
)
from core.views.report import ReportCreateView, ReportFileUploadView

__all__ = [
    "Kalmar32CreateView",
    "MachineCreateView",
    "MachineDeleteView",
    "MachineDetailView",
    "MachineDuplicateView",
    "MachineListView",
    "MachinePDFView",
    "MachineUpdateView",
    "ReportCreateView",
    "ReportFileUploadView",
]
