"""Views for managing manufacturers.

Includes listing, creating, updating, viewing, and deleting manufacturers.
"""

from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import ManufacturerForm
from core.models import Manufacturer


class ManufacturerListView(ListView):
    """Displays a list of all manufacturers."""

    model = Manufacturer
    template_name = "core/list.html"
    context_object_name = "manufacturers"
    paginate_by = 10

    def get_context_data(self, **kwargs: object) -> dict:
        """Add manufacturer cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": manufacturer.name,
                "subtitle": manufacturer.country,
                "view_url": reverse("manufacturer_detail", args=[manufacturer.pk]),
                "edit_url": reverse("manufacturer_edit", args=[manufacturer.pk]),
                "delete_url": reverse("manufacturer_delete", args=[manufacturer.pk]),
                "delete_confirm_message": f"Удалить {manufacturer.name}?",
            }
            for manufacturer in context["manufacturers"]
        ]
        context.update(
            {
                "title": "Производители",
                "items": items,
                "add_url": reverse("manufacturer_add"),
                "add_label": "Добавить производителя",
                "empty_message": "Производители не найдены.",
            },
        )
        return context

    def get_queryset(self) -> object:
        """Return a queryset of manufacturers filtered by the search query."""
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(country__icontains=q))
        return qs

class ManufacturerCreateView(CreateView):
    """Handles creation of a new manufacturer."""

    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("manufacturer_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for creating a manufacturer."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить производителя",
                "submit_label": "Создать",
            },
        )
        return context


class ManufacturerUpdateView(UpdateView):
    """Handles editing an existing manufacturer."""

    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("manufacturer_list")

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
                "fields": [
                    {"label": "Имя", "value": manufacturer.name},
                    {"label": "Страна", "value": manufacturer.country},
                    {"label": "Язык", "value": manufacturer.language},
                    {"label": "Телефон", "value": manufacturer.phone},
                ],
                "add_url": reverse("manufacturer_add"),
                "edit_url": reverse("manufacturer_edit", args=[manufacturer.pk]),
                "delete_url": reverse("manufacturer_delete", args=[manufacturer.pk]),
                "add_label": "Добавить нового производителя",
            },
        )
        return context


class ManufacturerDeleteView(DeleteView):
    """Handles deletion confirmation for a manufacturer."""

    model = Manufacturer
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("manufacturer_list")

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
