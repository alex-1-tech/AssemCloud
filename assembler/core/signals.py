"""Signal handlers for model change logging and initial role creation."""

from __future__ import annotations

from django.db import models
from django.db.models.signals import post_migrate, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict

from core.middleware import get_current_user
from core.models import ChangesLog, Role
from core.services import first_access_level, second_access_level


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
        return # New object, no changes to log

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
    roles = list(first_access_level) + list(second_access_level)

    for role in roles:
        Role.objects.get_or_create(name=role["name"], description=role["description"])
