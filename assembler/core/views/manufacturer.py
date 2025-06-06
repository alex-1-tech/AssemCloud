"""Views for managing manufacturers.

Includes listing, creating, updating, viewing, and deleting manufacturers.
"""
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

from core.forms import ManufacturerForm
from core.mixins import NextUrlMixin, QuerySetMixin
from core.models import Manufacturer

MANUFACTURER_LIST_URL = "manufacturer_list"

class ManufacturerListView(QuerySetMixin, ListView):
    """Displays a list of all manufacturers."""

    model = Manufacturer
    template_name = "core/list.html"
    context_object_name = "manufacturers"
    paginate_by = 7

    def get_context_data(self, **kwargs: object) -> dict:
        """Add manufacturer cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Производители",
                "items": self.get_manufacturer_items(
                    context["manufacturers"],
                ),
                "add_url": reverse("manufacturer_add"),
                "empty_message": "Производители не найдены.",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context

    def get_manufacturer_items(
        self, manufacturers: list[Manufacturer],
        ) -> list[dict[str, Any]]:
        """Generate a list of dictionary items.

        Representing client metadata for UI rendering.
        """
        return [
            {
                "title": manufacturer.name,
                "subtitle": manufacturer.country,
                "view_url": reverse("manufacturer_detail", args=[manufacturer.pk]),
                "edit_url": reverse(
                    "manufacturer_edit", args=[manufacturer.pk],
                    ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("manufacturer_delete", args=[manufacturer.pk]),
                "delete_confirm_message": f"Удалить {manufacturer.name}?",
            }
            for manufacturer in manufacturers
        ]

    def get_queryset(self) -> object:
        """Return a queryset of manufacturers filtered by the search query."""
        q = self.request.GET.get("q", "").strip()
        return self.get_queryset_default(
            q,
            Q(Q(name__icontains=q) | Q(country__icontains=q)),
        )

class ManufacturerCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new manufacturer."""

    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "core/edit.html"
    default_redirect_url_name = MANUFACTURER_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add context metadata for creating a manufacturer."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить производителя",
                "submit_label": "Создать",
            },
        )
        return context


class ManufacturerUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing manufacturer."""

    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "core/edit.html"
    default_redirect_url_name = MANUFACTURER_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for editing a manufacturer."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать производителя",
                "submit_label": "Сохранить",
            },
        )
        return context


class ManufacturerDetailView(DetailView):
    """Displays detailed information about a manufacturer."""

    model = Manufacturer
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs: object) -> dict:
        """Add manufacturer fields and actions to context."""
        context = super().get_context_data(**kwargs)
        manufacturer = self.object
        context.update(
            {
                "title": "Производитель",
                "subtitle": manufacturer.name,
                "fields": [
                    {"label": "Страна", "value": manufacturer.country},
                    {"label": "Язык", "value": manufacturer.language},
                    {"label": "Телефон", "value": manufacturer.phone},
                ],
                "add_url": reverse("manufacturer_add"),
                "edit_url": reverse(
                    "manufacturer_edit", args=[manufacturer.pk],
                    ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("manufacturer_delete", args=[manufacturer.pk]),
                "add_label": "Добавить нового производителя",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context


class ManufacturerDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a manufacturer."""

    model = Manufacturer
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = MANUFACTURER_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict:
        """Add confirmation message and actions to context."""
        context = super().get_context_data(**kwargs)
        manufacturer = self.object
        context.update(
            {
                "title": "Удалить производителя",
                "message": (
                    f"Вы уверены, что хотите удалить производителя {manufacturer.name}?"
                ),
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("manufacturer_detail", args=[manufacturer.pk]),
            },
        )
        return context
