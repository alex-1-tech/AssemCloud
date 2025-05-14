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
    CustomPasswordResetConfirmView,
    ResendVerificationView,
    UserDetailView,
    UserListView,
    UserLoginView,
    UserPasswordChangeView,
    UserRegisterView,
    UserUpdateView,
    verify_email_view,

    ManufacturerCreateView,
    ManufacturerListView,
    ManufacturerDetailView,
    ManufacturerUpdateView,
    ManufacturerDeleteView,

    PartCreateView,
    PartDeleteView,
    PartDetailView,
    PartListView,
    PartUpdateView,

    ClientCreateView,
    ClientListView,
    ClientDetailView,
    ClientUpdateView,
    ClientDeleteView,

    MachineCreateView,
    MachineListView,
    MachineDetailView,
    MachineUpdateView,
    MachineDeleteView,

    ModuleCreateView,
    ModuleListView,
    ModuleDetailView,
    ModuleUpdateView,
    ModuleDeleteView,

    BlueprintCreateView,
    BlueprintListView,
    BlueprintDetailView,
    BlueprintUpdateView,
    BlueprintDeleteView,

    ModulePartCreateView,
    ModulePartDeleteView,
    ModulePartDetailView,
    ModulePartListView,
    ModulePartUpdateView,
]
