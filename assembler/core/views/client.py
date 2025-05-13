from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import ClientForm  # Предполагается, что форма создана
from core.models import Client


class ClientListView(ListView):
    model = Client
    template_name = "core/list.html"
    context_object_name = "clients"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": client.name,
                "subtitle": client.country,
                "view_url": reverse("client_detail", args=[client.pk]),
                "edit_url": reverse("client_edit", args=[client.pk]),
                "delete_url": reverse("client_delete", args=[client.pk]),
                "delete_confirm_message": f"Удалить клиента {client.name}?",
            }
            for client in context["clients"]
        ]
        context.update({
            "title": "Клиенты",
            "items": items,
            "add_url": reverse("client_add"),
            "add_label": "Добавить клиента",
            "empty_message": "Клиенты не найдены.",
        })
        return context


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("client_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Добавить клиента",
            "submit_label": "Создать",
        })
        return context


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("client_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Редактировать клиента",
            "submit_label": "Сохранить",
        })
        return context


class ClientDetailView(DetailView):
    model = Client
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs):
        client = self.object
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Клиент",
            "fields": [
                {"label": "Имя клиента", "value": client.name},
                {"label": "Страна", "value": client.country},
                {"label": "Телефон", "value": client.phone},
            ],
            "edit_url": reverse("client_edit", args=[client.pk]),
            "delete_url": reverse("client_delete", args=[client.pk]),
        })
        return context


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("client_list")

    def get_context_data(self, **kwargs):
        client = self.object
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Удалить клиента",
            "message": f"Вы уверены, что хотите удалить клиента {client.name}?",
            "confirm_label": "Удалить",
            "cancel_label": "Отмена",
            "cancel_url": reverse("client_detail", args=[client.pk]),
        })
        return context
