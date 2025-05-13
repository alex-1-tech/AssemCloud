from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView as UserLogoutView
from django.urls import path

from .views import (
    CustomPasswordResetConfirmView,
    ResendVerificationView,
    UserDetailView,
    UserLoginView,
    UserPasswordChangeView,
    UserRegisterView,
    UserUpdateView,
    verify_email_view,
)

urlpatterns = [
    # users
    path("users/register/", UserRegisterView.as_view(), name="register"),
    path("users/login/", UserLoginView.as_view(), name="login"),
    path("users/logout/", UserLogoutView.as_view(next_page="login"), name="logout"),
    path("users/edit/", UserUpdateView.as_view(), name="user_edit"),
    path("users/detail/", UserDetailView.as_view(), name="user_profile"),
    # passwords
    path("password_change/", UserPasswordChangeView.as_view(), name="password_change"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="core/user/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="core/user/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(
            template_name="core/user/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="core/user/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # verify email
    path("verify/<str:uidb64>/<str:token>/", verify_email_view, name="verify_email"),
    path(
        "users/resend-verification/",
        ResendVerificationView.as_view(),
        name="resend_verification",
    ),
    # other
    path("", UserRegisterView.as_view(), name="register"),
]
