"""Views package exports for core application."""

from core.views.machine import (
    MachineCreateView,
    MachineDeleteView,
    MachineDetailView,
    MachineDuplicateView,
    MachineListView,
    MachinePDFView,
    MachineUpdateView,
)

__all__ = [
    "MachineCreateView",
    "MachineDeleteView",
    "MachineDetailView",
    "MachineDuplicateView",
    "MachineListView",
    "MachinePDFView",
    "MachineUpdateView",
]
