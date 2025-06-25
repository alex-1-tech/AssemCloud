"""Views for managing machine-module relationships.

Includes listing, creating, updating, viewing, and deleting machine-module links.
"""

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import MachineModuleForm
from core.models import MachineModule


class MachineModuleListView(ListView):
    """Displays a list of all machine-module relationships."""

    model = MachineModule
    template_name = "core/machineparts/list.html"
    context_object_name = "machinemodules"
    paginate_by = 7

    def get_context_data(self, **kwargs: object) -> dict:
        """Add machine-module cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": f"{mm.machine} — {mm.module}",
                "subtitle": f"Количество: {mm.quantity}",
                "view_url": reverse("machinemodule_detail", args=[mm.pk]),
                "edit_url": reverse("machinemodule_edit", args=[mm.pk]),
                "delete_url": reverse("machinemodule_delete", args=[mm.pk]),
                "delete_confirm_message": f"Удалить связь: {mm.machine} — {mm.module}?",
            }
            for mm in context["machinemodules"]
        ]
        context.update(
            {
                "title": "Количество модулей в машине",
                "items": items,
                "add_url": reverse("machinemodule_add"),
                "empty_message": "Связи не найдены.",
            }
        )
        context["user_roles"] = list(
            self.request.user.roles.values_list("role__name", flat=True),
        )
        return context

    def get_queryset(self) -> object:
        """Return a queryset of machinemodules filtered by the search query."""
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(machine__name__icontains=q) | Q(module__name__icontains=q),
            )
        return qs


class MachineModuleCreateView(CreateView):
    """Handles creation of a new machine-module relationship."""

    model = MachineModule
    form_class = MachineModuleForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("machinemodule_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for creating a machine-module relationship."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить модуль в машину",
                "submit_label": "Создать",
            }
        )
        return context

    def form_valid(self, form: MachineModuleForm) -> object:
        """Show success message on creation."""
        messages.info(self.request, "Успешно добавлено")
        return super().form_valid(form)


class MachineModuleUpdateView(UpdateView):
    """Handles editing an existing machine-module relationship."""

    model = MachineModule
    form_class = MachineModuleForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("machinemodule_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for editing a machne-module relationship."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать количество модулей",
                "submit_label": "Сохранить",
            }
        )
        return context

    def form_valid(self, form: MachineModuleForm) -> object:
        """Show success message on update."""
        messages.info(self.request, "Успешно изменено")
        return super().form_valid(form)


class MachineModuleDetailView(DetailView):
    """Displays detailed information about a machine-module relationship."""

    model = MachineModule
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs: object) -> dict:
        """Add module-part fields and actions to context."""
        context = super().get_context_data(**kwargs)
        obj = self.object
        name_machine = obj.machine.name if obj.machine else "—"
        name_module = obj.module.name if obj.module else "—"
        name = f"{name_machine} - {name_module}"
        context.update(
            {
                "title": "Количество модулей",
                "subtitle": name,
                "fields": [
                    {
                        "label": "Машина",
                        "value": name_machine,
                        "url": reverse("machine_detail", args=[obj.machine.pk]),
                    },
                    {
                        "label": "Модуль",
                        "value": name_module,
                        "url": reverse("module_detail", args=[obj.module.pk]),
                    },
                    {"label": "Количество", "value": obj.quantity},
                ],
                "add_url": reverse("machinemodule_add"),
                "edit_url": reverse("machinemodule_edit", args=[obj.pk]),
                "delete_url": reverse("machinemodule_delete", args=[obj.pk]),
                "add_label": "Добавить",
            }
        )
        context["user_roles"] = list(
            self.request.user.roles.values_list("role__name", flat=True),
        )
        return context


class MachineModuleDeleteView(DeleteView):
    """Handles deletion confirmation for a machine-module relationship."""

    model = MachineModule
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("machinemodule_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add confirmation message and actions to context."""
        context = super().get_context_data(**kwargs)
        obj = self.object
        context.update(
            {
                "title": "Удалить связь",
                "message": (
                    f"Вы уверены, что хотите удалить связь: {obj.machine} — {obj.module}?",
                ),
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("machinemodule_detail", args=[obj.pk]),
            }
        )
        return context
