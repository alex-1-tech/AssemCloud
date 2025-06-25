"""Models for task management, including tasks, attachments, and object links.

This module defines models related to task workflow:
- `Task`: the core task entity with sender, recipient, title, message, and priority.
- `TaskAttachment`: files associated with a task.
- `TaskLink`: string reference to related objects in the system (via model path).
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models.base import user_fk


class TaskAttachment(models.Model):
    """Model representing a file attached to a task."""

    task = models.ForeignKey(
        "Task",
        related_name="attachments",
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to="tasks/attachments/")

    def __str__(self) -> str:
        """Return the name of the attached file."""
        return self.file.name


class TaskLink(models.Model):
    """Model storing a link (path) to another model/object related to a task."""

    task = models.ForeignKey("Task", related_name="links", on_delete=models.CASCADE)
    model_path = models.CharField(
        max_length=255,
        verbose_name=_("Ссылка на объект"),
        help_text=_("core/<model>/<id>"),
    )

    def __str__(self) -> str:
        """Return the string path of the related model."""
        return self.model_path


class Task(models.Model):
    """Model representing a task sent from one user to another.

    Includes title, message, sender, recipient, priority, and related links/attachments.
    """

    sender = user_fk(
        related_name="sent_tasks",
        verbose_name=_("Отправитель"),
        help_text=_("Пользователь, отправивший задачу"),
    )

    recipient = user_fk(
        related_name="received_tasks",
        verbose_name=_("Получатель"),
        help_text=_("Пользователь, получающий задачу"),
    )

    title = models.CharField(
        _("Титульник"),
        max_length=100,
        help_text=_("Титульник задачи"),
    )

    message = models.TextField(
        _("Сообщение"),
    )

    class Priority(models.TextChoices):
        """Enumeration of task priority levels."""

        LOW = "low", _("Низкий")
        MEDIUM = "medium", _("Средний")
        HIGH = "high", _("Высокий")

    priority = models.CharField(
        _("Приоритет"),
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    class Status(models.TextChoices):
        """Enumeration of task status levels."""

        IN_PROGRESS = "in_progress", _("В процессе")
        ON_REVIEW = "on_review", _("На проверке")
        ACCEPTED = "accepted", _("Принята")
        REJECTED = "rejected", _("Отклонена")
        ABANDONED = "abandoned", _("Брошена")

    status = models.CharField(
        _("Состояние"),
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )

    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    sent_at = models.DateTimeField(_("Отправлено"), null=True, blank=True)
    due_date = models.DateField(_("Срок выполнения"), null=True, blank=True)

    class Meta:
        """Task metadata: database table name, ordering, verbose names and indexes."""

        db_table: ClassVar[str] = "tasks"
        ordering: ClassVar[list[str]] = ["title"]
        verbose_name: ClassVar[str] = _("Задача")
        verbose_name_plural: ClassVar[str] = _("Задачи")
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        """Return string representation with priority and title."""
        return f"{self.get_priority_display()}: {self.title}"

    def save(self, *args: object, **kwargs: object) -> None:
        """Auto-set sent_at if status is changed to ON_REVIEW."""
        if self.status == self.Status.ON_REVIEW and self.sent_at is None:
            self.sent_at = timezone.now()
        super().save(*args, **kwargs)
