"""URL configuration for the core application."""
from typing import ClassVar

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView as UserLogoutView
from django.urls import path

from core import views
from core.mixins import RoleRequiredMixin
from core.services import first_access_level, second_access_level
from core.views import (
    CustomPasswordResetConfirmView,
    MachineListView,
    ResendVerificationView,
    UserDetailView,
    UserListView,
    UserLoginView,
    UserPasswordChangeView,
    UserRegisterView,
    UserUpdateView,
    dashboard_view,
    part_create_view,
    verify_email_view,
)
from core.views.task import TaskCompleteView, TaskReopenView

# users
urlpatterns = [
    path("users/register/", UserRegisterView.as_view(), name="register"),
    path("users/login/", UserLoginView.as_view(), name="login"),
    path("users/logout/", UserLogoutView.as_view(next_page="login"), name="logout"),
    path("users/edit/<int:pk>/", UserUpdateView.as_view(), name="user_edit"),
    path(
        "users/detail/<int:pk>/",
        UserDetailView.as_view(),
        name="user_profile",
    ),
    path("users/list/", UserListView.as_view(), name="user_list"),
]

# passwords
urlpatterns += [
    path("password_change/", UserPasswordChangeView.as_view(), name="password_change"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="core/user/password_reset.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="core/user/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(
            template_name="core/user/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="core/user/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]

# verify email
urlpatterns += [
    path("verify/<str:uidb64>/<str:token>/", verify_email_view, name="verify_email"),
    path(
        "users/resend-verification/",
        ResendVerificationView.as_view(),
        name="resend_verification",
    ),
]

# objects
model_names = [
    "manufacturer",
    "part",
    "client",
    "machine",
    "module",
    "modulepart",
    "task",
]

view_types = {
    "list": "ListView",
    "add": "CreateView",
    "edit": "UpdateView",
    "detail": "DetailView",
    "delete": "DeleteView",
}

def create_role_view(view_class: object) -> object:
    """Wrap a given Django view class with role-based access control.

    This function dynamically creates and returns a new view class that inherits
    from both `RoleRequiredMixin` and the specified `view_class`. The returned
    view class restricts access to users who have at least one of the predefined roles:
    "Директор", "Конструктор", "Тестировщик", or "Программист".
    """
    class WithRoleView(RoleRequiredMixin, view_class):
            """A view class that restricts access to users with specific roles.

            Inherits from RoleRequiredMixin and a generic view class (`view_class`).
            Only users who have at least one of the specified roles are allowed access.
            """

            required_roles: ClassVar[list[str]] = list(first_access_level.keys())

    if view_class.__name__ not in [
        "ClientCreateView",
        "ClientUpdateView",
        "ClientDeleteView",
    ]:
        WithRoleView.required_roles += list(second_access_level.keys())
    return WithRoleView

for model in model_names:
    class_prefix = model.capitalize()  # "manufacturer" → "Manufacturer"

    if class_prefix == "Modulepart":  # исключение
        class_prefix = "ModulePart"

    for action, suffix in view_types.items():
        class_name = f"{class_prefix}{suffix}"  # e.g. ManufacturerListView
        view_class = getattr(views, class_name)

        WithRoleView = create_role_view(view_class=view_class)

        if action == "list":
            pattern = f"{model}s/"
        elif action == "add":
            pattern = f"{model}s/add/"
        elif action == "edit":
            pattern = f"{model}s/<int:pk>/edit/"
        elif action == "detail":
            pattern = f"{model}s/<int:pk>/"
        elif action == "delete":
            pattern = f"{model}s/<int:pk>/delete/"
        current_path = path(
            pattern, WithRoleView.as_view(), name=f"{model}_{action}",
        )

        if model == "machine" and action == "delete":
            continue

        if model == "part" and action in {"add", "edit"}:
            current_path = path(
                pattern,
                part_create_view,
            name=f"{model}_{action}",
            )

        urlpatterns.append(current_path)

# Добавляем url для завершения задачи
urlpatterns.append(
    path(
        "tasks/<int:pk>/complete/",
        create_role_view(TaskCompleteView).as_view(),
        name="task_complete",
    ),
)
urlpatterns.append(
    path(
        "tasks/<int:pk>/reopen/",
        create_role_view(TaskReopenView).as_view(),
        name="task_reopen",
    ),
)

BaseWithRoleView = create_role_view(view_class=MachineListView)

urlpatterns += [
    # other
    path("", login_required(dashboard_view), name="dashboard"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
