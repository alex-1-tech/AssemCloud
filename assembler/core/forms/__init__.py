from core.forms.blueprint import BlueprintForm
from core.forms.client import ClientForm
from core.forms.machine import MachineForm
from core.forms.manufacturer import ManufacturerForm
from core.forms.module import ModuleForm
from core.forms.modulepart import ModulePartForm
from core.forms.part import PartForm
from core.forms.user import (
    UserLoginForm,
    UserPasswordChangeForm,
    UserRegistrationForm,
    UserSetPasswordForm,
    UserUpdateForm,
)

__all__ = [
    UserLoginForm,
    UserPasswordChangeForm,
    UserRegistrationForm,
    UserSetPasswordForm,
    UserUpdateForm,
    ManufacturerForm,
    PartForm,
    ModulePartForm,
    BlueprintForm,
    ClientForm,
    MachineForm,
    ModuleForm,
]
