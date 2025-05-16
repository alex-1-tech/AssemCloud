"""Mixin for role-based access control in Django class-based views.

This module provides RoleRequiredMixin, which extends Django's LoginRequiredMixin
to restrict access to views based on user roles. The mixin checks if the
authenticated user has at least one of the required roles before allowing access.

Example usage:
    class SomeView(RoleRequiredMixin, View):
        required_roles = ["admin", "manager"]
"""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse, HttpResponseRedirect


class RoleRequiredMixin(LoginRequiredMixin):
    """Mixin that restricts access to users who have specific roles.

    Extends LoginRequiredMixin to first require authentication, then
    checks if the user has any of the roles listed in `required_roles`.
    If the user lacks required roles, raises PermissionDenied.
    """

    required_roles: ClassVar[list[str]] = []

    def dispatch(
            self, request: HttpRequest,
            *args: object,
            **kwargs: object,
        ) -> (HttpResponseRedirect | HttpResponse):
        """Override dispatch method to enforce role-based access control."""
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        user_roles = user.roles.all().select_related("role")
        user_role_names = {user_role.role.name for user_role in user_roles}

        if not any(role in user_role_names for role in self.required_roles):
            error_msg = "У вас нет доступа к этому разделу.\
                \nДля дополнительной информации обратитесь к администратору."
            raise PermissionDenied(error_msg)

        return super().dispatch(request, *args, **kwargs)
