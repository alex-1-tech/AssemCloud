"""Base utilities and abstract models.

For normalization, phone validation and user-related tracking fields.

This module includes common validators, reusable mixins for field normalization,
timestamp tracking, and a helper for user foreign key definition.
"""
from __future__ import annotations

from typing import Callable

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# === Validators ===

PHONE_VALIDATOR = RegexValidator(
    regex=r"^\+?\d{9,15}$",
    message=_("Номер телефона должен быть в формате: '+99999999999'. От 9 до 15 цифр."),
)


# === Foreign Key Helper ===

def user_fk(related_name: str, verbose_name: str) -> models.ForeignKey:
    """Return a ForeignKey to the User model with standardized parameters."""
    return models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name=related_name,
        verbose_name=verbose_name,
    )


# === Abstract Models ===

class TimeStampedModelWithUser(models.Model):
    """Abstract model with created/updated timestamps and user references."""

    created_on = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Создано"),
        help_text=_("Дата и время создания записи."),
    )

    updated_on = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Обновлено"),
        help_text=_("Дата и время последнего обновления записи."),
    )

    created_by = user_fk("%(class)s_created", _("Создано пользователем"))
    updated_by = user_fk("%(class)s_updated", _("Обновлено пользователем"))

    class Meta:
        """Model metadata for TimeStampedModelWithUser."""

        abstract = True


class ReprMixin(models.Model):
    """Abstract mixin providing __repr__ method with class name and ID."""

    class Meta:
        """Model metadata for ReprMixin."""

        abstract = True

    def __repr__(self) -> str:
        """Return representation like: <ClassName 42>."""
        return f"<{self.__class__.__name__} {self.pk}>"


# === Normalization Utilities ===

def normalize_phone(value: str|None) -> str|None:
    """Remove spaces from phone number and trim it."""
    return value.replace(" ", "").strip() if value else value


def normalize_email(value: str|None) -> str|None:
    """Normalize email to lowercase and trim."""
    return value.lower().strip() if value else value


def normalize_country(value: str|None) -> str|None:
    """Convert country code to uppercase and trim."""
    return value.upper().strip() if value else value


def normalize_language(value: str|None) -> str|None:
    """Convert language code to lowercase and trim."""
    return value.lower().strip() if value else value


def normalize_name(value: str|None) -> str|None:
    """Trim leading and trailing whitespace."""
    return value.strip() if value else value


# === Normalization Mixin ===

class NormalizeMixin(models.Model):
    """Abstract mixin that automatically normalizes field values on clean().

    It searches for `normalize_<field_name>` methods and applies them
    during validation.
    """

    class Meta:
        """Model metadata for NormalizeMixin."""

        abstract = True

    def clean(self) -> None:
        """Apply normalization to all fields before validation."""
        super().clean()

        for field in self._meta.fields:
            field_name = field.name
            normalize_method: Callable|None = getattr(
                self,
                f"normalize_{field_name}",
                None,
            )
            if callable(normalize_method):
                value = getattr(self, field_name)
                if value is not None:
                    setattr(self, field_name, normalize_method(value))

    # Static normalization methods for reuse

    @staticmethod
    def normalize_email(value: str) -> str:
        """Normalize email: strip whitespace and lowercase."""
        return normalize_email(value)

    @staticmethod
    def normalize_phone(value: str) -> str:
        """Normalize phone: remove spaces and trim."""
        return normalize_phone(value)

    @staticmethod
    def normalize_country(value: str) -> str:
        """Normalize country: convert to uppercase."""
        return normalize_country(value)

    @staticmethod
    def normalize_language(value: str) -> str:
        """Normalize language: convert to lowercase."""
        return normalize_language(value)

    @staticmethod
    def normalize_name(value: str) -> str:
        """Normalize name: trim leading/trailing whitespace."""
        return normalize_name(value)

    @staticmethod
    def normalize_version(value: str) -> str:
        """Normalize version: trim whitespace."""
        return normalize_name(value)
