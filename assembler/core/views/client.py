"""Views for managing clients.

Includes listing, creating, updating, viewing, and deleting clients.
"""

from __future__ import annotations

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

from core.forms import ClientForm
from core.mixins import NextUrlMixin, QuerySetMixin
from core.models import Client

CLIENT_LIST_URL = "client_list"


class ClientListView(QuerySetMixin, ListView):
    """Displays a list of all clients."""

    model = Client
    template_name = "core/list.html"
    context_object_name = "clients"
    paginate_by = 7

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add client cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Клиенты",
                "items": self.get_client_items(context["clients"]),
                "add_url": reverse("client_add"),
                "empty_message": "Клиенты не найдены.",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context

    def get_client_items(self, clients: list[Client]) -> list[dict[str, Any]]:
        """Generate a list of dictionary items.

        Representing client metadata for UI rendering.
        """
        return [
            {
                "title": client.name,
                "subtitle": client.country,
                "view_url": reverse("client_detail", args=[client.pk]),
                "edit_url": reverse(
                    "client_edit",
                    args=[client.pk],
                )
                + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("client_delete", args=[client.pk]),
                "delete_confirm_message": f"Удалить клиента {client.name}?",
            }
            for client in clients
        ]

    def get_queryset(self) -> object:
        """Return a queryset of clients filtered by the search query."""
        q = self.request.GET.get("q", "").strip()
        return self.get_queryset_default(
            q,
            Q(name__icontains=q) | Q(country__icontains=q),
        )


class ClientCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new client."""

    model = Client
    form_class = ClientForm
    template_name = "core/edit.html"
    default_redirect_url_name = CLIENT_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add context metadata for creating a client."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить клиента",
                "submit_label": "Создать",
            },
        )
        return context

    def form_valid(self, form: ClientForm) -> object:
        """Show success message on creation."""
        messages.info(self.request, "Успешно добавлено")
        return super().form_valid(form)


class ClientUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing client."""

    model = Client
    form_class = ClientForm
    template_name = "core/edit.html"
    default_redirect_url_name = CLIENT_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add context metadata for editing a client."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать клиента",
                "submit_label": "Сохранить",
            },
        )
        return context

    def form_valid(self, form: ClientForm) -> object:
        """Show success message on update."""
        messages.info(self.request, "Успешно изменено")
        return super().form_valid(form)


class ClientDetailView(DetailView):
    """Displays detailed information about a client."""

    model = Client
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add client fields and actions to context."""
        client = self.object
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Клиент",
                "subtitle": client.name,
                "fields": [
                    {"label": "Страна", "value": client.country},
                    {"label": "Телефон", "value": client.phone},
                ],
                "edit_url": reverse(
                    "client_edit",
                    args=[client.pk],
                )
                + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("client_delete", args=[client.pk]),
                "add_url": reverse("client_add"),
                "add_label": "Добавить нового клиента",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context


class ClientDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a client."""

    model = Client
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = CLIENT_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add confirmation message and actions to context."""
        client = self.object
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Удалить клиента",
                "message": f"Вы уверены, что хотите удалить клиента {client.name}?",
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("client_detail", args=[client.pk]),
            },
        )
        return context
