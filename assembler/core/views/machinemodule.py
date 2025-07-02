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
from core.mixins import NextUrlMixin
from core.models import MachineModule

MACHINEMODULE_LIST_URL = "machinemodule_list"

def get_full_name(machinemodule: MachineModule) -> str:
    """Return machinemodule full name."""
    if machinemodule.machine:
        return f"{machinemodule.machine.name} <-> {machinemodule.module.name}"
    if machinemodule.parent:
        return f"{machinemodule.parent.name} <-> {machinemodule.module.name}"
    return "-"

class MachineModuleListView(ListView):
    """Displays a list of all machine-module relationships."""

    model = MachineModule
    template_name = "core/machinemodules/list.html"
    context_object_name = "machinemodules"
    paginate_by = 7

    def get_context_data(self, **kwargs: object) -> dict:
        """Add machine-module cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": get_full_name(mm),
                "subtitle": f"Количество: {mm.quantity}",
                "view_url": reverse("machinemodule_detail", args=[mm.pk]),
                "edit_url": reverse("machinemodule_edit", args=[mm.pk]),
                # "delete_url": reverse("machinemodule_delete", args=[mm.pk]),
                # "delete_confirm_message": f"Удалить связь: {get_full_name(mm)}?",
            }
            for mm in context["machinemodules"]
        ]
        context.update(
            {
                "title": "Количество модулей в машине",
                "items": items,
                "add_url": reverse("machinemodule_add"),
                "empty_message": "Связи не найдены.",
            },
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


class MachineModuleCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new machine-module relationship."""

    model = MachineModule
    form_class = MachineModuleForm
    template_name = "core/edit.html"
    default_redirect_url_name = MACHINEMODULE_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for creating a machine-module relationship."""
        context = super().get_context_data(**kwargs)

        title = "-"
        if "parent" in context["form"].fields:
            title = "Добавить подмодуль в модуль"
        elif "machine" in context["form"].fields:
            title = "Добавить модуль в машину"
        context.update(
            {
                "title": title,
                "submit_label": "Создать",
            },
        )
        return context

    def form_valid(self, form: MachineModuleForm) -> object:
        """Save the form manually and add the missing fields."""
        messages.info(self.request, "Успешно добавлено")
        return super().form_valid(form)

    def get_initial(self) -> dict[str, object]:
        """Return initial data for the form from GET if present."""
        initial = super().get_initial()
        machine = self.request.GET.get("machine")
        parent = self.request.GET.get("parent")
        mode = self.request.GET.get("mode")
        if machine:
            initial["machine"] = machine
        if parent:
            initial["parent"] = parent
        if mode:
            initial["mode"] = mode
        return initial


class MachineModuleUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing machine-module relationship."""

    model = MachineModule
    form_class = MachineModuleForm
    template_name = "core/edit.html"
    default_redirect_url_name = MACHINEMODULE_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata for editing a machne-module relationship."""
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Редактировать количество модулей",
                "submit_label": "Сохранить",
            },
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
        context.update(
            {
                "title": "Количество модулей",
                "subtitle": get_full_name(obj),
                "fields": self.get_fields(obj),
                "add_url": reverse("machinemodule_add"),
                "edit_url": reverse("machinemodule_edit", args=[obj.pk]),
                "delete_url": reverse("machinemodule_delete", args=[obj.pk]),
                "add_label": "Добавить",
            },
        )
        context["user_roles"] = list(
            self.request.user.roles.values_list("role__name", flat=True),
        )
        return context

    def get_fields(self, machine_module: MachineModule) -> list[dict[str, object]]:
        """Construct a list of field metadata."""
        name_module = machine_module.module.name if machine_module.module else "—"

        fields = []

        # Add machine in fields
        if machine_module.machine:
            name_machine = (
                f"{machine_module.machine.name} {machine_module.machine.version}"
            )
            fields.append(
                {
                    "label": "Машина",
                    "value": name_machine,
                    "url": reverse("machine_detail", args=[machine_module.machine.pk]),
                },
            )

        # Add parent in fields
        if machine_module.parent:
            name_parent = (
                machine_module.parent.name
                if machine_module.parent
                else "-"
            )
            fields.append(
                {
                    "label": "Родительский модуль",
                    "value": name_parent,
                    "url": reverse(
                        "module_detail", args=[machine_module.parent.pk],
                    ),
                },
            )

        # Add module and quintity in fields
        fields += [
            {
                "label": "Модуль",
                "value": name_module,
                "url": reverse("module_detail", args=[machine_module.module.pk]),
            },
            {"label": "Количество", "value": machine_module.quantity},
        ]
        return fields


class MachineModuleDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a machine-module relationship."""

    model = MachineModule
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = MACHINEMODULE_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict:
        """Add confirmation message and actions to context."""
        context = super().get_context_data(**kwargs)
        obj = self.object
        context.update(
            {
                "title": "Удалить связь",
                "message": (
                    f"Вы уверены, что хотите удалить связь:\
                         {obj.machine} — {obj.module}?",
                ),
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("machinemodule_detail", args=[obj.pk]),
            },
        )
        return context
