"""Views package exports for core application."""

from core.views.client import (
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
)
from core.views.dashboard import dashboard_view
from core.views.machine import (
    MachineCreateView,
    MachineDeleteView,
    MachineDetailView,
    MachineListView,
    MachineUpdateView,
)
from core.views.machine_import import (
    MachineImportProcessView,
    MachineImportSelectView,
)
from core.views.machinemodule import (
    MachineModuleCreateView,
    MachineModuleDeleteView,
    MachineModuleDetailView,
    MachineModuleListView,
    MachineModuleUpdateView,
)
from core.views.machinemoduleset import (
    module_create_view,
    module_edit_view,
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
from core.views.module_import import (
    ModuleImportProcessView,
    ModuleImportSelectView,
)
from core.views.modulepart import (
    ModulePartCreateView,
    ModulePartDeleteView,
    ModulePartDetailView,
    ModulePartListView,
    ModulePartUpdateView,
)
from core.views.modulepartset import part_create_view, part_edit_view
from core.views.part import (
    PartCreateView,
    PartDeleteView,
    PartDetailView,
    PartListView,
    PartUpdateView,
)
from core.views.task import (
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)
from core.views.telegrambot import ToggleTelegramNotificationsView, telegram_webhook
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
    "ClientCreateView",
    "ClientDeleteView",
    "ClientDetailView",
    "ClientListView",
    "ClientUpdateView",
    "CustomPasswordResetConfirmView",
    "MachineCreateView",
    "MachineDeleteView",
    "MachineDetailView",
    "MachineImportProcessView",
    "MachineImportSelectView",
    "MachineListView",
    "MachineModuleCreateView",
    "MachineModuleDeleteView",
    "MachineModuleDetailView",
    "MachineModuleListView",
    "MachineModuleUpdateView",
    "MachineUpdateView",
    "ManufacturerCreateView",
    "ManufacturerDeleteView",
    "ManufacturerDetailView",
    "ManufacturerListView",
    "ManufacturerUpdateView",
    "ModuleCreateView",
    "ModuleDeleteView",
    "ModuleDetailView",
    "ModuleImportProcessView",
    "ModuleImportSelectView",
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
    "TaskCreateView",
    "TaskDeleteView",
    "TaskDetailView",
    "TaskListView",
    "TaskUpdateView",
    "ToggleTelegramNotificationsView",
    "UserDetailView",
    "UserListView",
    "UserLoginView",
    "UserPasswordChangeView",
    "UserRegisterView",
    "UserUpdateView",
    "dashboard_view",
    "module_create_view",
    "module_edit_view",
    "part_create_view",
    "part_edit_view",
    "telegram_webhook",
    "verify_email_view",
]
