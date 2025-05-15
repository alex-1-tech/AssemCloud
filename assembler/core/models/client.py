"""Models for managing clients and manufacturers.

This module provides models to represent clients and manufacturers,
including their basic contact information
such as name, country, language, and phone number.
"""

from typing import ClassVar

from core.models.base import PHONE_VALIDATOR, NormalizeMixin, ReprMixin, _, models


class Client(ReprMixin, NormalizeMixin, models.Model):
    """Model representing a client organization or customer.

    Stores basic client details including name, country, and contact phone number.
    Each client must have a unique name. The phone number is optional and validated.
    """

    name = models.CharField(
        _("Имя клиента"),
        max_length=150,
        unique=True,
        help_text=_("Название клиента (уникальное значение)"),
    )

    country = models.CharField(
        _("Страна"),
        max_length=100,
        help_text=_("Страна клиента"),
    )

    phone = models.CharField(
        _("Телефон"),
        max_length=20,
        blank=True,
        validators=[PHONE_VALIDATOR],
        help_text=_("Контактный телефон клиента (необязательное поле)"),
    )

    def __str__(self) -> str:
        """Return the client`s name and country."""
        return f"{self.name} ({self.country})" if self.country else self.name

    class Meta:
        """Model metadata for Client."""

        db_table: ClassVar[str] = "clients"
        verbose_name: ClassVar[str] = _("Клиент")
        verbose_name_plural: ClassVar[str] = _("Клиенты")
        ordering: ClassVar[list[str]] = ["name"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["name"]),
            models.Index(fields=["country"]),
        ]


class Manufacturer(ReprMixin, NormalizeMixin, models.Model):
    """Model representing a product manufacturer.

    Stores manufacturer information such as name, country of origin,
    preferred communication language, and contact phone number.
    The name must be unique across manufacturers.
    """

    name = models.CharField(
        _("Название производителя"),
        max_length=150,
        unique=True,
        help_text=_("Название производителя (уникальное значение)"),
    )

    country = models.CharField(
        _("Страна"),
        max_length=100,
        help_text=_("Страна, в которой расположен производитель"),
    )

    language = models.CharField(
        _("Язык"),
        max_length=50,
        blank=True,
        help_text=_("Язык общения с производителем (необязательно)"),
    )

    phone = models.CharField(
        _("Телефон"),
        max_length=20,
        blank=True,
        validators=[PHONE_VALIDATOR],
        help_text=_("Контактный телефон производителя (необязательное поле)"),
    )

    def __str__(self) -> str:
        """Return the manufacturer`s name and country."""
        return f"{self.name} ({self.country})" if self.country else self.name

    class Meta:
        """Model metadata for Manufacturer."""

        db_table: ClassVar[str] = "manufacturers"
        verbose_name: ClassVar[str] = _("Производитель")
        verbose_name_plural: ClassVar[str] = _("Производители")
        ordering: ClassVar[list[str]] = ["name"]
