from django.urls import re_path, path
from django.contrib.auth.views import LogoutView as UserLogoutView
from django.contrib.auth import views as auth_views
from .views import (
    UserRegisterView, UserLoginView,
    UserUpdateView, UserDetailView,
    UserPasswordChangeView,
)

urlpatterns = [
    # users
    re_path(r"^users/register/$", UserRegisterView.as_view(), name="register"),
    re_path(r"^users/login/$", UserLoginView.as_view(), name="login"),
    re_path(r"^users/logout/$", UserLogoutView.as_view(next_page="login"), name="logout"),
    re_path(r"^users/edit/$", UserUpdateView.as_view(), name="user_edit"),
    re_path(r"^users/detail/$", UserDetailView.as_view(), name="user_profile"),

    # passwords
    re_path(r"^password_change/$", UserPasswordChangeView.as_view(), name="password_change"),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='core/user/password_reset.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/user/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/user/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/user/password_reset_complete.html'
    ), name='password_reset_complete'),

    # other
    path("", UserRegisterView.as_view(), name="register"),
]
