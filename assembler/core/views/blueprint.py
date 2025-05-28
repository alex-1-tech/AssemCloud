"""Views for managing blueprints.

Includes listing, creating, updating, viewing, and deleting blueprints.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models import Q
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import BlueprintForm
from core.mixins import NextUrlMixin, QuerySetMixin
from core.models import Blueprint

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

BLUEPRINT_LIST_URL = "blueprint_list"

def user_profile_url(user: AbstractBaseUser | None) -> str | None:
    """Return the URL to the user's profile page."""
    return reverse("user_profile", args=[user.pk]) if user else None

class BlueprintListView(QuerySetMixin, ListView):
    """Displays a list of all blueprints."""

    model = Blueprint
    template_name = "core/list.html"
    context_object_name = "blueprints"
    paginate_by = 7

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add blueprint cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Чертежи",
                "items": self.get_blueprint_items(context["blueprints"]),
                "add_url": reverse("blueprint_add"),
                "empty_message": "Чертежи не найдены.",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context

    def get_blueprint_items(
        self, blueprints: list[Blueprint],
        ) -> list[dict[str, Any]]:
        """Generate a list of dictionary items.

        Representing blueprint metadata for UI rendering.
        """
        return [
            {
                "title": str(bp.naming_scheme),
                "subtitle": str(bp.version),
                "view_url": reverse("blueprint_detail", args=[bp.pk]),
                "edit_url": reverse(
                    "blueprint_edit", args=[bp.pk],
                    ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("blueprint_delete", args=[bp.pk]),
                "delete_confirm_message": f"Удалить чертеж {bp}?",
            }
            for bp in blueprints
        ]

    def get_queryset(self) -> object:
        """Return a queryset of blueprints filtered by the search query."""
        q = self.request.GET.get("q", "").strip()
        return self.get_queryset_default(
            q,
            Q(Q(naming_scheme__icontains=q) | Q(version__icontains=q)),
        )

class BlueprintCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new blueprint."""

    model = Blueprint
    form_class = BlueprintForm
    template_name = "core/blueprints/edit.html"
    default_redirect_url_name = BLUEPRINT_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add context metadata for creating a blueprint."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить чертеж",
                "submit_label": "Создать",
            },
        )
        return context


class BlueprintUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing blueprint."""

    model = Blueprint
    form_class = BlueprintForm
    template_name = "core/blueprints/edit.html"
    default_redirect_url_name = BLUEPRINT_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add context metadata for editing a blueprint."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать чертеж",
                "submit_label": "Сохранить",
            },
        )
        return context


class BlueprintDetailView(DetailView):
    """Displays detailed information about a blueprint."""

    model = Blueprint
    template_name = "core/blueprints/detail.html"

    def get_blueprint_fields(
        self, bp: Blueprint,
        ) -> list[dict[str, Any]]:
        """Construct a list of field metadata.

        For displaying blueprint attributes in the UI.
        """
        module = bp.module if hasattr(bp, "module") else None
        url_module = reverse("module_detail",args=[module.id]) if module else None
        return [
            {"label": "Вес", "value": bp.weight},
            {"label": "Масштаб", "value": bp.scale},
            {
                "label": "Модуль",
                "value": module,
                "url": url_module,
            },
            {
                "label": "Разработчик",
                "value": str(bp.developer) if bp.developer else "—",
                "url": user_profile_url(bp.developer),
            },
            {
                "label": "Проверяющий",
                "value": str(bp.validator) if bp.validator else "—",
                "url": user_profile_url(bp.validator),
            },
            {
                "label": "Ведущий конструктор",
                "value": str(bp.lead_designer) if bp.lead_designer else "—",
                "url": user_profile_url(bp.lead_designer),
            },
            {
                "label": "Главный конструктор",
                "value": str(bp.chief_designer) if bp.chief_designer else "—",
                "url": user_profile_url(bp.chief_designer),
            },
            {
                "label": "Утвердивший",
                "value": str(bp.approver) if bp.approver else "—",
                "url": user_profile_url(bp.approver),
            },
        ]

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add blueprint fields, file URLs, user profiles, and actions to context."""
        bp = self.object
        request = self.request
        context = super().get_context_data(**kwargs)

        scheme_url: str | None = request.build_absolute_uri(bp.scheme_file.url) \
            if bp.scheme_file else None
        step_url: str | None = request.build_absolute_uri(bp.step_file.url) \
            if bp.step_file else None

        context.update(
            {
                "title": "Чертеж",
                "scheme_url": scheme_url,
                "step_url": step_url,
                "subtitle": f"{bp.naming_scheme} - {bp.version}",
                "fields": self.get_blueprint_fields(bp),
                "add_url": reverse("blueprint_add"),
                "edit_url": reverse(
                    "blueprint_edit", args=[bp.pk],
                    ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("blueprint_delete", args=[bp.pk]),
                "add_label": "Добавить новый чертеж",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )

        return context


class BlueprintDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a blueprint."""

    model = Blueprint
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = BLUEPRINT_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add confirmation message and actions to context."""
        bp = self.object
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Удалить чертеж",
                "message": f"Вы уверены, что хотите удалить чертеж {bp}?",
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("blueprint_detail", args=[bp.pk]),
            },
        )
        return context
