from core.views.manufacturer import (
    ManufacturerCreateView,
    ManufacturerDeleteView,
    ManufacturerDetailView,
    ManufacturerListView,
    ManufacturerUpdateView,
)
from core.views.user import (
    CustomPasswordResetConfirmView,
    ResendVerificationView,
    UserDetailView,
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
]
