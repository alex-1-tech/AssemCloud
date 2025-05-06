from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import ChangesLog
from django.db import models
from core.middleware import get_current_user


@receiver(pre_save)
def log_model_changes(sender, instance, **kwargs):
    if 'django.contrib.sessions' in sender.__module__:
        return
    
    if not issubclass(sender, models.Model) or sender._meta.abstract:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # если создали новый объект ( не изменили )
        # то отменить
        return

    old_data = model_to_dict(old_instance)
    new_data = model_to_dict(instance)

    for field, old_value in old_data.items():
        new_value = new_data.get(field)
        if old_value != new_value:
                # фильтры
                if sender.__name__ == 'User' and str(field) == 'last_login':
                     continue
                
                # создание лога
                ChangesLog.objects.create(
                    table_name=sender.__name__,
                    record_id=str(instance.pk),
                    column_name=field,
                    old_value=str(old_value),
                    new_value=str(new_value),
                    changed_by=get_current_user(),
                )
