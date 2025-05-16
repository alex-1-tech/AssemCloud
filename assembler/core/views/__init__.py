"""Views package exports for core application."""

from core.views.blueprint import (
    BlueprintCreateView,
    BlueprintDeleteView,
    BlueprintDetailView,
    BlueprintListView,
    BlueprintUpdateView,
)
from core.views.client import (
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
)
from core.views.machine import (
    MachineCreateView,
    MachineDeleteView,
    MachineDetailView,
    MachineListView,
    MachineUpdateView,
)
from core.views.manufacturer import (
    ManufacturerCreateView,
    ManufacturerDeleteView,
    ManufacturerDetailView,
    ManufacturerListView,
    ManufacturerUpdateView,
)
from core.views.module import (
    ModuleCreateView,
    ModuleDeleteView,
    ModuleDetailView,
    ModuleListView,
    ModuleUpdateView,
)
from core.views.modulepart import (
    ModulePartCreateView,
    ModulePartDeleteView,
    ModulePartDetailView,
    ModulePartListView,
    ModulePartUpdateView,
)
from core.views.modulepartset import part_create_view
from core.views.part import (
    PartCreateView,
    PartDeleteView,
    PartDetailView,
    PartListView,
    PartUpdateView,
)
from core.views.user import (
    CustomPasswordResetConfirmView,
    ResendVerificationView,
    UserDetailView,
    UserListView,
    UserLoginView,
    UserPasswordChangeView,
    UserRegisterView,
    UserUpdateView,
    verify_email_view,
)

__all__ = [
    "BlueprintCreateView",
    "BlueprintDeleteView",
    "BlueprintDetailView",
    "BlueprintListView",
    "BlueprintUpdateView",
    "ClientCreateView",
    "ClientDeleteView",
    "ClientDetailView",
    "ClientListView",
    "ClientUpdateView",
    "CustomPasswordResetConfirmView",
    "MachineCreateView",
    "MachineDeleteView",
    "MachineDetailView",
    "MachineListView",
    "MachineUpdateView",
    "ManufacturerCreateView",
    "ManufacturerDeleteView",
    "ManufacturerDetailView",
    "ManufacturerListView",
    "ManufacturerUpdateView",
    "ModuleCreateView",
    "ModuleDeleteView",
    "ModuleDetailView",
    "ModuleListView",
    "ModulePartCreateView",
    "ModulePartDeleteView",
    "ModulePartDetailView",
    "ModulePartListView",
    "ModulePartUpdateView",
    "ModuleUpdateView",
    "PartCreateView",
    "PartDeleteView",
    "PartDetailView",
    "PartListView",
    "PartUpdateView",
    "ResendVerificationView",
    "UserDetailView",
    "UserListView",
    "UserLoginView",
    "UserPasswordChangeView",
    "UserRegisterView",
    "UserUpdateView",
    "part_create_view",
    "verify_email_view",
]

