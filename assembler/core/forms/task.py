"""Module defining TaskForm for handling Task model forms.

This module contains the TaskForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Task model.
"""

from typing import ClassVar

from django import forms

from core.forms.base import BaseStyledForm
from core.models import Task, User


class TaskForm(BaseStyledForm):
    """Form for creating or updating a Task instance."""

    placeholders: ClassVar[dict[str, str]] = {
        "title": "Введите заголовок задачи",
        "message": "Опишите суть задачи",
        "due_date": "До какого числа нужно выполнить",
    }

    select2_fields: ClassVar[dict[str, tuple]] = {
        "recipient": (User, (
            "first_name__icontains",
            "last_name__icontains",
            "email__icontains",
        )),
    }

    class Meta:
        """Metadata for TaskForm."""

        model = Task
        fields = (
            "title",
            "message",
            "priority",
            "recipient",
            "due_date",
        )

        widgets: ClassVar[dict[str, object]] = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
