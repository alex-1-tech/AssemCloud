"""Views package exports for core application."""

from core.views.kalmar32 import (
    Kalmar32CreateView,
    Kalmar32GetReportsView,
    Kalmar32RetrieveView,
)
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
    "Kalmar32GetReportsView",
    "Kalmar32RetrieveView",
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
