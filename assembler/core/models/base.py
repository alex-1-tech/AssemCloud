from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db import models


PHONE_VALIDATOR = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message=_("Номер телефона должен быть в формате: '+99999999999'. От 9 до 15 цифр.")
)

def user_fk(related_name, verbose_name):
    return models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name=related_name,
        verbose_name=verbose_name
    )

class TimeStampedModelWithUser(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    created_by = user_fk("%(class)s_created", _("Создано пользователем"))
    updated_by = user_fk("%(class)s_updated", _("Обновлено пользователем"))

    class Meta:
        abstract = True

class ReprMixin(models.Model):
    class Meta:
        abstract = True

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.pk}>"

def normalize_phone(value):
    return value.replace(" ", "").strip() if value else value


def normalize_email(value):
    return value.lower().strip() if value else value


def normalize_country(value):
    return value.upper()


def normalize_language(value):
    return value.lower()

def normalize_name(value):
    return value.strip()


class NormalizeMixin(models.Model):
    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        for field in self._meta.fields:
            field_name = field.name
            normalize_method = getattr(self, f'normalize_{field_name}', None)
            if callable(normalize_method):
                value = getattr(self, field_name)
                if value is not None:
                    setattr(self, field_name, normalize_method(value))

    @staticmethod
    def normalize_email(value):
        return normalize_email(value)

    @staticmethod
    def normalize_phone(value):
        return normalize_phone(value)

    @staticmethod
    def normalize_country(value):
        return normalize_country(value)

    @staticmethod
    def normalize_language(value):
        return normalize_language(value)

    @staticmethod
    def normalize_name(value):
        return normalize_name(value)

    @staticmethod
    def normalize_version(value):
        return normalize_name(value)
