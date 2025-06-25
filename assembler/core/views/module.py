"""Views for managing modules.

Includes listing, creating, updating, viewing, and deleting modules.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Q
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.mixins import NextUrlMixin, QuerySetMixin
from core.models import Module
from core.services.assembly_tree import build_module_tree

MODULE_LIST_URL = "module_list"


class ModuleListView(QuerySetMixin, ListView):
    """Displays a list of all modules."""

    model = Module
    template_name = "core/list.html"
    context_object_name = "modules"
    paginate_by = 7

    def get_context_data(self, **kwargs: object) -> dict:
        """Add module cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Модули",
                "items": self.get_module_items(context["modules"]),
                "add_url": reverse("module_add"),
                "empty_message": "Модули не найдены.",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context

    def get_module_items(
        self,
        modules: list[Module],
    ) -> list[dict[str, Any]]:
        """Generate a list of dictionary items.

        Representing client metadata for UI rendering.
        """
        return [
            {
                "title": module.name,
                "view_url": reverse("module_detail", args=[module.pk]),
                "edit_url": reverse(
                    "module_edit",
                    args=[module.pk],
                )
                + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("module_delete", args=[module.pk]),
                "delete_confirm_message": f"Удалить модуль {module.name}?",
            }
            for module in modules
        ]

    def get_queryset(self) -> object:
        """Return a queryset of clients filtered by the search query."""
        q = self.request.GET.get("q", "").strip()
        return self.get_queryset_default(
            q,
            Q(Q(name__icontains=q) | Q(decimal__icontains=q)),
        )


class ModuleCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new module."""

    pass  # noqa: PIE790


class ModuleUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing module."""

    pass  # noqa: PIE790


class ModuleDetailView(DetailView):
    """Displays detailed information about a module."""

    model = Module
    template_name = "core/modules/detail.html"

    def get_module_fields(
        self,
        module: Module,
    ) -> list[dict[str, Any]]:
        """Construct a list of field metadata.

        For displaying module attributes in the UI.
        """
        return [
            {"label": "Децимальный номер", "value": module.decimal},
            {
                "label": "Производитель",
                "value": module.manufacturer.name
                if module.manufacturer
                else "Производитель не указан",
                "url": reverse(
                    "manufacturer_detail",
                    args=[module.manufacturer.pk],
                )
                if module.manufacturer
                else None,
            },
            {"label": "Статус", "value": module.get_module_status_display()},
        ]

    def get_context_data(self, **kwargs: object) -> dict:
        """Add module fields and actions to context."""
        module = self.object
        request = self.request
        context = super().get_context_data(**kwargs)

        scheme_url: str | None = (
            request.build_absolute_uri(module.scheme_file.url)
            if module.scheme_file
            else None
        )
        step_url: str | None = (
            request.build_absolute_uri(module.step_file.url)
            if module.step_file
            else None
        )
        module_tree = build_module_tree(module)
        print(module_tree)
        context.update(
            {
                "title": "Модуль",
                "subtitle": f"{module.name} - {module.version}",
                "fields": self.get_module_fields(module),
                "scheme_url": scheme_url,
                "step_url": step_url,
                "module_tree": module_tree,
                "add_url": reverse("module_add"),
                "edit_url": reverse(
                    "module_edit",
                    args=[module.pk],
                )
                + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("module_delete", args=[module.pk]),
                "add_label": "Добавить новый модуль",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context


class ModuleDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a module."""

    model = Module
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = MODULE_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict:
        """Add confirmation message and actions to context."""
        context = super().get_context_data(**kwargs)
        module = self.object
        context.update(
            {
                "title": "Удалить модуль",
                "message": f"Вы уверены, что хотите удалить модуль {module.name}?",
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("module_detail", args=[module.pk]),
            },
        )
        return context
