"""Forms package exports for core application."""

from core.forms.client import ClientForm
from core.forms.machine import MachineForm
from core.forms.machinemodule import MachineModuleForm
from core.forms.machinemoduleset import MachineModuleFormSet
from core.forms.manufacturer import ManufacturerForm
from core.forms.module import ModuleForm
from core.forms.modulepart import ModulePartForm
from core.forms.modulepartset import ModulePartFormSet
from core.forms.part import PartForm
from core.forms.task import TaskForm
from core.forms.user import (
    UserLoginForm,
    UserPasswordChangeForm,
    UserRegistrationForm,
    UserSetPasswordForm,
    UserUpdateForm,
)

__all__ = [
    "ClientForm",
    "MachineForm",
    "MachineModuleForm",
    "MachineModuleFormSet",
    "ManufacturerForm",
    "ModuleForm",
    "ModulePartForm",
    "ModulePartFormSet",
    "PartForm",
    "TaskForm",
    "UserLoginForm",
    "UserPasswordChangeForm",
    "UserRegistrationForm",
    "UserSetPasswordForm",
    "UserUpdateForm",
]
