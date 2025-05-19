"""Views for managing modules.

Includes listing, creating, updating, viewing, and deleting modules.
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

from core.forms import ModuleForm
from core.models import Module
from core.services.assembly_tree import build_module_tree


class ModuleListView(ListView):
    """Displays a list of all modules."""

    model = Module
    template_name = "core/list.html"
    context_object_name = "modules"
    paginate_by = 10

    def get_context_data(self, **kwargs: object) -> dict:
        """Add module cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": module.name,
                "subtitle": f"s/n: {module.serial}",
                "view_url": reverse("module_detail", args=[module.pk]),
                "edit_url": reverse("module_edit", args=[module.pk]),
                "delete_url": reverse("module_delete", args=[module.pk]),
                "delete_confirm_message": f"Удалить модуль {module.name}?",
            }
            for module in context["modules"]
        ]
        context.update(
            {
                "title": "Модули",
                "items": items,
                "add_url": reverse("module_add"),
                "add_label": "Добавить модуль",
                "empty_message": "Модули не найдены.",
            },
        )
        return context

    def get_queryset(self) -> object:
        """Return a queryset of modules filtered by the search query."""
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(serial__icontains=q))
        return qs

class ModuleCreateView(CreateView):
    """Handles creation of a new module."""

    model = Module
    form_class = ModuleForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("module_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for creating a module."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить модуль",
                "submit_label": "Создать",
            },
        )
        return context

    def get_initial(self) -> dict:
        """Add initial metadata for creating a module."""
        initial = super().get_initial()
        machine_id = self.request.GET.get("machine")
        parent_id  = self.request.GET.get("parent")
        if machine_id:
            initial["machine"] = machine_id
        if parent_id:
            initial["parent"] = parent_id
        return initial

class ModuleUpdateView(UpdateView):
    """Handles editing an existing module."""

    model = Module
    form_class = ModuleForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("module_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for editing a module."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать модуль",
                "submit_label": "Сохранить",
            },
        )
        return context


class ModuleDetailView(DetailView):
    """Displays detailed information about a module."""

    model = Module
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs: object) -> dict:
        """Add module fields and actions to context."""
        context = super().get_context_data(**kwargs)
        module = self.object
        context.update(
            {
                "title": "Модуль",
                "fields": [
                    {"label": "Название модуля", "value": module.name},
                    {
                        "label": "Машина",
                        "value": module.machine,
                        "url": reverse("machine_detail",args=[module.machine.pk]),
                    },
                    {
                        "label": "Артикул",
                        "value": module.part_number or "Артикул не указан",
                    },
                    {"label": "Серийный номер", "value": module.serial},
                    {
                        "label": "Производитель",
                        "value": module.manufacturer.name \
                            if module.manufacturer else "Производитель не указан",
                        "url": reverse(
                            "manufacturer_detail", args=[module.manufacturer.pk],
                            ) if module.manufacturer else None,
                    },
                    {"label": "Версия", "value": module.version},
                    {"label": "Статус", "value": module.get_module_status_display()},
                    {
                        "label": "Чертёж",
                        "value": module.blueprint.naming_scheme \
                            if module.blueprint else "Чертеж не указан",
                        "url": reverse("blueprint_detail", args=[module.blueprint.pk]) \
                            if module.blueprint else None,
                    },
                    {
                        "label": "Родительский модуль",
                        "value": module.parent.name \
                            if module.parent else "Нет родителя",
                        "url": reverse("module_detail", args=[module.parent.pk]) \
                            if module.parent else None,
                    },
                ],
                "module_tree": build_module_tree(module),
                "add_url": reverse("module_add"),
                "edit_url": reverse("module_edit", args=[module.pk]),
                "delete_url": reverse("module_delete", args=[module.pk]),
                "add_label": "Добавить новый модуль",
            },
        )
        return context


class ModuleDeleteView(DeleteView):
    """Handles deletion confirmation for a module."""

    model = Module
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("module_list")

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
