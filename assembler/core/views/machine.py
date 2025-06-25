"""Views for managing machines.

Includes listing, creating, updating, viewing, and deleting machines.
"""

from typing import Any

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import MachineForm
from core.mixins import NextUrlMixin, QuerySetMixin
from core.models import Machine
from core.services.assembly_tree import build_machine_tree

MACHINE_LIST_URL = "machine_list"


class MachineListView(QuerySetMixin, ListView):
    """Displays a list of all machines."""

    model = Machine
    template_name = "core/list.html"
    context_object_name = "machines"
    paginate_by = 7

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add machine cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Машины",
                "items": self.get_machine_items(context["machines"]),
                "add_url": reverse("machine_add"),
                "empty_message": "Ничего не найдено по вашему запросу."
                if self.request.GET.get("q")
                else None,
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context

    def get_machine_items(
        self,
        machines: list[Machine],
    ) -> list[dict[str, Any]]:
        """Generate a list of dictionary items.

        Representing machine metadata for UI rendering.
        """
        return [
            {
                "title": machine.name,
                "subtitle": machine.version,
                "status": machine.get_status_display(),
                "view_url": reverse("machine_detail", args=[machine.pk]),
                "edit_url": reverse(
                    "machine_edit",
                    args=[machine.pk],
                )
                + f"?next={self.request.get_full_path()}",
                "delete_confirm_message": f"Удалить машину {machine.name}?",
            }
            for machine in machines
        ]

    def get_queryset(self) -> object:
        """Return a queryset of machines filtered by the search query."""
        q = self.request.GET.get("q", "").strip()
        return self.get_queryset_default(
            q,
            Q(Q(name__icontains=q) | Q(version__icontains=q)),
        )


class MachineCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new machine."""

    model = Machine
    form_class = MachineForm
    template_name = "core/edit.html"
    default_redirect_url_name = MACHINE_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add context metadata for creating a machine."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить машину",
                "submit_label": "Создать",
            },
        )
        return context

    def form_valid(self, form: MachineForm) -> object:
        """Show success message on creation."""
        messages.info(self.request, "Успешно добавлено")
        return super().form_valid(form)


class MachineUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing machine."""

    model = Machine
    form_class = MachineForm
    template_name = "core/edit.html"
    default_redirect_url_name = MACHINE_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add context metadata for editing a machine."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать машину",
                "submit_label": "Сохранить",
            },
        )
        return context

    def form_valid(self, form: MachineForm) -> object:
        """Show success message on update."""
        messages.info(self.request, "Успешно изменено")
        return super().form_valid(form)


class MachineDetailView(DetailView):
    """Displays detailed information about a machine."""

    model = Machine
    template_name = "core/machines/detail.html"

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add machine fields, tree, and actions to context."""
        machine = self.object
        machine_tree = build_machine_tree(machine)
        print(machine_tree)
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Машина",
                "subtitle": f"{machine.name} - {machine.version}",
                "fields": [
                    {
                        "label": "Клиенты",
                        "value": machine.clients.all(),
                        "url": "client_detail",
                        "is_links": True,
                    },
                ],
                "status": machine.get_status_display(),
                "machine_tree": machine_tree,
                "edit_url": reverse(
                    "machine_edit",
                    args=[machine.pk],
                )
                + f"?next={self.request.get_full_path()}",
                "add_url": reverse("machine_add"),
                "add_label": "Добавить новую машину",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context


class MachineDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a machine."""

    pass  # noqa: PIE790
    '''
    model = Machine
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("machine_list")
    default_redirect_url_name = MACHINE_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add confirmation message and actions to context."""
        machine = self.object
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Удалить машину",
                "message": f"Вы уверены, что хотите удалить машину {machine.name}?",
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("machine_detail", args=[machine.pk]),
            },
        )
        return context
    '''
