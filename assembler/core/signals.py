from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import ChangesLog
from django.db import models
from core.middleware import get_current_user

@receiver(pre_save)
def log_model_changes(sender, instance, **kwargs):
    if not issubclass(sender, models.Model) or sender._meta.abstract:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_data = model_to_dict(old_instance)
    new_data = model_to_dict(instance)

    for field, old_value in old_data.items():
        new_value = new_data.get(field)
        if old_value != new_value:
            ChangesLog.objects.create(
                model_name=sender.__name__,
                object_id=str(instance.pk),
                field=field,
                old_value=str(old_value),
                new_value=str(new_value),
                changed_by=get_current_user(),
            )
