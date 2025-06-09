"""Views for managing parts.

Includes listing, creating, updating, viewing, and deleting parts.
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
from core.models import Part

PART_LIST_URL = "part_list"

class PartListView(QuerySetMixin, ListView):
    """Displays a list of all parts."""

    model = Part
    template_name = "core/list.html"
    context_object_name = "items"
    paginate_by = 7

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata and card items for listing parts."""
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Изделия",
                "items": self.get_part_items(context["items"]),
                "add_url": reverse("part_add"),
                "empty_message": "Изделия не найдены.",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context

    def get_part_items(
        self, parts: list[Part],
        ) -> list[dict[str, Any]]:
        """Generate a list of dictionary items.

        Representing part metadata for UI rendering.
        """
        return [
            {
                "title": part.name,
                "subtitle": (
                    "Производитель: "
                    f"{part.manufacturer.name if part.manufacturer else 'не указан'}"
                ),
                "view_url": reverse("part_detail", args=[part.pk]),
                "edit_url": reverse(
                    "part_edit", args=[part.pk],
                    ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("part_delete", args=[part.pk]),
                "delete_confirm_message": f"Удалить изделие {part.name}?",
            }
            for part in parts
        ]


    def get_queryset(self) -> object:
        """Return a queryset of clients filtered by the search query."""
        q = self.request.GET.get("q", "").strip()
        return self.get_queryset_default(
            q,
            Q(Q(name__icontains=q) | Q(manufacturer__name__icontains=q)),
        )


class PartCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new part."""

    pass  # noqa: PIE790



class PartUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing part."""

    pass  # noqa: PIE790

class PartDetailView(DetailView):
    """Displays detailed information about a part."""

    model = Part
    template_name = "core/detail.html"

    def get_part_fields(
        self, part: Part,
        ) -> list[dict[str, Any]]:
        """Construct a list of field metadata.

        For displaying part attributes in the UI.
        """
        return [
            {"label": "Описание", "value": part.description or "Нет описания"},
            {"label": "Материал", "value": part.material or "Не указан"},
            {
                "label": "Дата производства",
                "value": part.manufacture_date or "Не указана",
            },
            {
                "label": "Модули",
                "value": [
                    {
                        "name": mp.module.name,
                        "url": reverse("module_detail", args=[mp.module.pk]),
                        "quantity": mp.quantity,
                    }
                    for mp in part.part_modules.select_related("module")
                ],
                "is_links": True,
            },
        ]

    def get_context_data(self, **kwargs: object) -> dict:
        """Add part fields and actions to context."""
        context = super().get_context_data(**kwargs)
        part = self.object
        context.update(
            {
                "title": "Изделие",
                "subtitle": part.name,
                "fields": self.get_part_fields(part),
                "add_url": reverse("part_add"),
                "edit_url": reverse(
                    "part_edit", args=[part.pk],
                ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("part_delete", args=[part.pk]),
                "add_label": "Добавить новое изделие",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context


class PartDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a part."""

    model = Part
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = PART_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict:
        """Add confirmation message and actions to context."""
        context = super().get_context_data(**kwargs)
        part = self.object
        context.update(
            {
                "title": "Удалить изделие",
                "message": f"Вы уверены, что хотите удалить изделие {part.name}?",
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("part_detail", args=[part.pk]),
            },
        )
        return context
