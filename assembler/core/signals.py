"""Signal handlers for model change logging and initial role creation."""

from __future__ import annotations

from django.db import models
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict

from core.middleware import get_current_user
from core.models import ChangesLog, Role, Task
from core.services import first_access_level, second_access_level, send_telegram_message


@receiver(pre_save)
def log_model_changes(
    sender: type[models.Model],
    instance: models.Model,
    **kwargs: dict[str, object],  # noqa: ARG001
) -> None:
    """Log changes to model instances before saving."""
    if "django.contrib.sessions" in sender.__module__:
        return

    if not issubclass(sender, models.Model) or getattr(sender, "is_abstract", False):
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return  # New object, no changes to log

    old_data = model_to_dict(old_instance)
    new_data = model_to_dict(instance)

    for field, old_value in old_data.items():
        new_value = new_data.get(field)
        if old_value != new_value:
            # filters
            if sender.__name__ == "User" and str(field) == "last_login":
                continue

            # create log
            ChangesLog.objects.create(
                table_name=sender.__name__,
                record_id=str(instance.pk),
                column_name=field,
                old_value=str(old_value),
                new_value=str(new_value),
                changed_by=get_current_user(),
            )


@receiver(post_migrate)
def create_roles(sender: object, **kwargs: dict[str, object]) -> None:  # noqa: ARG001
    """Create default roles after migrations."""
    roles = first_access_level | second_access_level

    for role in roles:
        Role.objects.get_or_create(name=role, description=roles[role])


@receiver(pre_save, sender=Task)
def cache_old_status(instance: Task, **kwargs: dict[str, object]) -> None:  # noqa: ARG001
    """Кэширует старый статус задачи перед сохранением."""
    if instance.pk:
        try:
            old_instance = Task.objects.get(pk=instance.pk)
            instance.old_status = old_instance.status
        except Task.DoesNotExist:
            instance.old_status = None
    else:
        instance.old_status = None


@receiver(post_save, sender=Task)
def send_task_to_telegram(
    instance: Task,
    created: bool,  # noqa: FBT001
    **kwargs: dict[str, object],  # noqa: ARG001
) -> None:
    """Оповещение в Telegram при создании или изменении статуса задачи."""
    chat_id = getattr(instance.recipient, "telegram_chat_id", None)
    wants_notifications = getattr(
        instance.recipient,
        "wants_telegram_notifications",
        False,
    )
    if not chat_id or not wants_notifications:
        return
    if created:
        message = f"🆕 Новая задача:\n<b>{instance.title}</b>\n\n"
        send_telegram_message(message, chat_id=chat_id)
    else:
        old_status = getattr(instance, "old_status", None)
        if old_status is not None and old_status != instance.status:
            message = (
                f"i Статус задачи <b>{instance.title}</b> изменён на: "
                f"<b>{instance.status}</b>"
            )
            send_telegram_message(message, chat_id=chat_id)
