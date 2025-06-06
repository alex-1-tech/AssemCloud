"""Reusable mixins for Django class-based views.

Mixins: role-based access control and flexible post-submit redirection.

This module provides two mixins:

1. RoleRequiredMixin:
    - Extends Django's LoginRequiredMixin to include role-based access control.
    - Requires that an authenticated user has at least one role listed in the view's
        `required_roles` attribute.
    - If the user does not have any of the required roles, access is denied with a
        PermissionDenied exception.

Example:
        class DashboardView(RoleRequiredMixin, View):
            required_roles = ["admin", "manager"]

2. NextUrlMixin:
    - Provides a flexible mechanism for redirecting after successful form submission.
    - If a `next` parameter is present in GET or POST data and is safe, the user is
        redirected to that URL.
    - Otherwise, the user is redirected to a default route defined
        by `default_redirect_url_name`.

Example:
        class ClientCreateView(NextUrlMixin, CreateView):
            default_redirect_url_name = "client_list"

These mixins are designed to reduce boilerplate and improve clarity in view definitions.

"""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

if TYPE_CHECKING:
    from django.db.models import Q
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

class NextUrlMixin:
    """A reusable view mixin that handles redirection after successful form submission.

    This mixin checks if a "next" URL is provided in either GET or POST parameters and
    whether it is safe (i.e., belongs to the same host and scheme). If the "next"
    parameter is valid, it redirects to that URL; otherwise, it redirects to a default
    URL defined by the `default_redirect_url_name` attribute.
    """

    default_redirect_url_name: str = ""

    def get_default_success_url(self) -> str:
        """Return the fallback URL.

        To redirect to if the "next" parameter is not provided
        or is not allowed.
        """
        if not self.default_redirect_url_name:
            msg = "You must define 'default_redirect_url_name'\
                 in the view or override 'get_default_success_url'."
            raise NotImplementedError(
                msg,
            )
        return reverse(self.default_redirect_url_name)

    def get_success_url(self) -> str:
        """Determine the URL to redirect to after a successful form submission."""
        next_url = (
            self.request.GET.get("next")
        )
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return self.get_default_success_url()

class QuerySetMixin:
    """A reusable mixin that adds basic search functionality.

    Mixin to Django class-based views that operate on querysets.
    """

    def get_search_query(self) -> str:
        """Retrieve and clean the search query from the request."""
        return self.request.GET.get("q", "").strip()

    def get_queryset_default(
        self, q: object, search_field: Q | None,
        ) -> object:
        """Return the filtered queryset based on the search query.

        Assumes `self.search_field` is a Q object already containing the query.
        """
        qs = super().get_queryset()
        if q and search_field:
            qs = qs.filter(search_field)
        return qs
