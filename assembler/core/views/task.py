"""Views for managing tasks.

Includes listing, creating, updating, viewing, and deleting tasks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import TaskForm
from core.mixins import NextUrlMixin, QuerySetMixin
from core.models import Task

if TYPE_CHECKING:
    from django import forms
    from django.http import HttpRequest, HttpResponse

TASK_LIST_URL = "dashboard"


class TaskListView(QuerySetMixin, ListView):
    """Displays a list of all tasks."""

    model = Task
    template_name = "core/list.html"
    context_object_name = "tasks"
    paginate_by = 7

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add task cards and metadata to context."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Задачи",
                "items": self.get_task_items(context["tasks"]),
                "add_url": reverse("task_add"),
                "empty_message": "Задачи не найдены.",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context

    def get_task_items(self, tasks: list[Task]) -> list[dict[str, Any]]:
        """Generate a list of dictionary items representing task metadata."""
        return [
            {
                "title": task.title,
                "subtitle": f"{task.get_priority_display()}\
                     — {task.get_status_display()}",
                "view_url": reverse("task_detail", args=[task.pk]),
                "edit_url": reverse(
                    "task_edit", args=[task.pk],
                    ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("task_delete", args=[task.pk]),
                "delete_confirm_message": f"Удалить задачу '{task.title}'?",
            }
            for task in tasks
        ]

    def get_queryset(self) -> object:
        """Return a queryset of tasks filtered by the search query."""
        q = self.request.GET.get("q", "").strip()
        return self.get_queryset_default(
            q,
            Q(title__icontains=q) | Q(message__icontains=q),
        )


class TaskCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new task."""

    model = Task
    form_class = TaskForm
    template_name = "core/tasks/edit.html"
    default_redirect_url_name = TASK_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add context metadata for creating a task."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить задачу",
                "submit_label": "Создать",
            },
        )
        return context

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        """Set the sender of the task to the currently logged-in user before saving."""
        form.instance.sender = self.request.user
        messages.info(self.request, "Успешно создано")
        return super().form_valid(form)

    def get_initial(self) -> dict[str, object]:
        """Return initial data for the form, including due_date from GET if present."""
        initial = super().get_initial()
        due_date = self.request.GET.get("due_date")
        if due_date:
            initial["due_date"] = due_date
        return initial


class TaskUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing task."""

    model = Task
    form_class = TaskForm
    template_name = "core/tasks/edit.html"
    default_redirect_url_name = TASK_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add context metadata for editing a task."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать задачу",
                "submit_label": "Сохранить",
            },
        )
        return context

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        """Ensure recipient is set: use form value or keep old if not provided."""
        if not form.cleaned_data.get("recipient"):
            form.instance.recipient = self.object.recipient
        messages.info(self.request, "Успешно изменено")
        return super().form_valid(form)

    def get_initial(self) -> dict[str, object]:
        """Return initial data for the form, including current recipient id."""
        initial = super().get_initial()
        if self.object and hasattr(self.object, "recipient") and self.object.recipient:
            initial["recipient"] = self.object.recipient.pk
        return initial


class TaskDetailView(DetailView):
    """Displays detailed information about a task."""

    model = Task
    template_name = "core/tasks/detail.html"

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add task fields and actions to context."""
        task = self.object
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Задача",
                "subtitle": task.title,
                "fields": [
                    {"label": "Отправитель", "value": str(task.sender)},
                    {"label": "Получатель", "value": str(task.recipient)},
                    {"label": "Сообщение", "value": task.message},
                    {"label": "Приоритет", "value": task.get_priority_display()},
                    {"label": "Статус", "value": task.get_status_display()},
                    {
                        "label": "Создана",
                        "value": task.created_at.strftime("%d.%m.%Y %H:%M"),
                    },
                    {
                        "label": "Завершена",
                        "value": task.completed_at.strftime(
                            "%d.%m.%Y %H:%M") if task.completed_at else "—",
                        },
                    {
                        "label": "Срок выполнения",
                        "value": task.due_date.strftime(
                            "%d.%m.%Y") if task.due_date else "—",
                        },
                ],
                "edit_url": reverse(
                    "task_edit", args=[task.pk],
                    ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("task_delete", args=[task.pk]),
                "add_url": reverse("task_add"),
                "add_label": "Добавить новую задачу",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context


class TaskDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a task."""

    model = Task
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = TASK_LIST_URL

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """Add confirmation message and actions to context."""
        task = self.object
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Удалить задачу",
                "message": f"Вы уверены, что хотите удалить задачу '{task.title}'?",
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("task_detail", args=[task.pk]),
            },
        )
        return context


class TaskCompleteView(UpdateView):
    """Handles marking a task as complete."""

    model = Task
    fields: ClassVar[list] = []

    def post(
        self,
        request: HttpRequest,
        *args: tuple[Any, ...],  # noqa: ARG002
        **kwargs: dict[str, Any],  # noqa: ARG002
    ) -> HttpResponse:
        """Mark the task as complete."""
        task = self.get_object()
        if not task.completed_at:
            task.completed_at = timezone.now()
            task.status = Task.Status.COMPLETED
            task.save()
            messages.success(request, "Задача успешно завершена.")
        return redirect("task_detail", pk=task.pk)

    def get(
        self,
        request: HttpRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> HttpResponse:
        """Allow GET to trigger the same as POST for convenience."""
        return self.post(request, *args, **kwargs)


class TaskReopenView(UpdateView):
    """Handles reopening a completed task (sets completed_at to None)."""

    model = Task
    fields: ClassVar[list] = []

    def post(
        self,
        request: HttpRequest,
        *args: tuple[Any, ...],  # noqa: ARG002
        **kwargs: dict[str, Any],  # noqa: ARG002
    ) -> HttpResponse:
        """Reopen the task by clearing completed_at.

        Sets status to in_progress.
        """
        task = self.get_object()
        if task.completed_at:
            task.completed_at = None
            task.status = Task.Status.IN_PROGRESS
            task.save()
            messages.success(request, "Задача возвращена в процесс.")
        return redirect("task_detail", pk=task.pk)

    def get(
        self,
        request: HttpRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> HttpResponse:
        """Allow GET to trigger the same as POST for convenience."""
        return self.post(request, *args, **kwargs)
