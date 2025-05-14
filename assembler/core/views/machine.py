from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import MachineForm
from core.models import Machine
from core.services.assembly_tree import build_machine_tree


class MachineListView(ListView):
    model = Machine
    template_name = "core/list.html"
    context_object_name = "machines"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": machine.name,
                "subtitle": machine.version,
                "view_url": reverse("machine_detail", args=[machine.pk]),
                "edit_url": reverse("machine_edit", args=[machine.pk]),
                "delete_url": reverse("machine_delete", args=[machine.pk]),
                "delete_confirm_message": f"Удалить машину {machine.name}?",
            }
            for machine in context["machines"]
        ]
        context.update({
            "title": "Машины",
            "items": items,
            "add_url": reverse("machine_add"),
            "add_label": "Добавить машину",
            "empty_message": "Машины не найдены.",
        })
        return context


class MachineCreateView(CreateView):
    model = Machine
    form_class = MachineForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("machine_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Добавить машину",
            "submit_label": "Создать",
        })
        return context


class MachineUpdateView(UpdateView):
    model = Machine
    form_class = MachineForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("machine_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Редактировать машину",
            "submit_label": "Сохранить",
        })
        return context


class MachineDetailView(DetailView):
    model = Machine
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs):
        machine = self.object
        machine_tree = build_machine_tree(machine)
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Машина",
            "fields": [
                {"label": "Название машины", "value": machine.name},
                {"label": "Версия", "value": machine.version},
                {
                    "label": "Клиенты", 
                    "value": ", ".join(
                        [client.name for client in machine.clients.all()]
                    )
                },
            ],
            "machine_tree": machine_tree,
            "edit_url": reverse("machine_edit", args=[machine.pk]),
            "delete_url": reverse("machine_delete", args=[machine.pk]),
        })
        return context


class MachineDeleteView(DeleteView):
    model = Machine
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("machine_list")

    def get_context_data(self, **kwargs):
        machine = self.object
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Удалить машину",
            "message": f"Вы уверены, что хотите удалить машину {machine.name}?",
            "confirm_label": "Удалить",
            "cancel_label": "Отмена",
            "cancel_url": reverse("machine_detail", args=[machine.pk]),
        })
        return context
