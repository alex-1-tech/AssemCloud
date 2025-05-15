"""Views for managing module-part relationships.

Includes listing, creating, updating, viewing, and deleting module-part links.
"""

from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import ModulePartForm
from core.models import ModulePart


class ModulePartListView(ListView):
    """Displays a list of all module-part relationships."""

    model = ModulePart
    template_name = "core/list.html"
    context_object_name = "moduleparts"

    def get_context_data(self, **kwargs: object) -> dict:
        """Add module-part cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": f"{mp.module} — {mp.part}",
                "subtitle": f"Количество: {mp.quantity}",
                "view_url": reverse("modulepart_detail", args=[mp.pk]),
                "edit_url": reverse("modulepart_edit", args=[mp.pk]),
                "delete_url": reverse("modulepart_delete", args=[mp.pk]),
                "delete_confirm_message": f"Удалить связь: {mp.module} — {mp.part}?",
            }
            for mp in context["moduleparts"]
        ]
        context.update(
            {
                "title": "Связи Модуль-Деталь",
                "items": items,
                "add_url": reverse("modulepart_add"),
                "add_label": "Добавить связь",
                "empty_message": "Связи не найдены.",
            },
        )
        return context


class ModulePartCreateView(CreateView):
    """Handles creation of a new module-part relationship."""

    model = ModulePart
    form_class = ModulePartForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("modulepart_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for creating a module-part relationship."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить связь Модуль-Деталь",
                "submit_label": "Создать",
            },
        )
        return context


class ModulePartUpdateView(UpdateView):
    """Handles editing an existing module-part relationship."""

    model = ModulePart
    form_class = ModulePartForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("modulepart_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for editing a module-part relationship."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать связь Модуль-Деталь",
                "submit_label": "Сохранить",
            },
        )
        return context


class ModulePartDetailView(DetailView):
    """Displays detailed information about a module-part relationship."""

    model = ModulePart
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs: object) -> dict:
        """Add module-part fields and actions to context."""
        context = super().get_context_data(**kwargs)
        obj = self.object
        context.update(
            {
                "title": "Связь Модуль-Деталь",
                "fields": [
                    {
                        "label": "Модуль",
                        "value": obj.module.name if obj.module else "—",
                    },
                    {"label": "Деталь", "value": obj.part.name if obj.part else "—"},
                    {"label": "Количество", "value": obj.quantity},
                ],
                "edit_url": reverse("modulepart_edit", args=[obj.pk]),
                "delete_url": reverse("modulepart_delete", args=[obj.pk]),
            },
        )
        return context


class ModulePartDeleteView(DeleteView):
    """Handles deletion confirmation for a module-part relationship."""

    model = ModulePart
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("modulepart_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add confirmation message and actions to context."""
        context = super().get_context_data(**kwargs)
        obj = self.object
        context.update(
            {
                "title": "Удалить связь",
                "message": (
                    f"Вы уверены, что хотите удалить связь: {obj.module} — {obj.part}?"
                ),
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("modulepart_detail", args=[obj.pk]),
            },
        )
        return context
