"""Models for storing information about modules and their attributes.

This module defines the `Module` model, which represents components of a machine.
It includes technical and manufacturing information such as blueprint,
part number, serial number, version, status, and links to manufacturer
and parent module (for nested module structures).
"""

from typing import ClassVar

from django.core.validators import MinLengthValidator

from core.models.base import (
    NormalizeMixin,
    ReprMixin,
    TimeStampedModelWithUser,
    _,
    models,
)
from core.models.client import Manufacturer


class Module(ReprMixin, NormalizeMixin, TimeStampedModelWithUser):
    """Model representing a machine module with various attributes.

    Modules can represent standalone or nested components within machines,
    with references to blueprints, manufacturers, anфd hierarchical relationships.

    Includes details like serial number, part number, name, version, description,
    and a defined status indicating the module's development stage.
    """

    machine = models.ForeignKey(
        "Machine",
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name=_("Машина"),
        blank=False,
        null=False,
    )

    blueprint = models.OneToOneField(
        "Blueprint",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Чертёж"),
    )

    part_number = models.CharField(
        _("Артикул"),
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(3)],
    )

    serial = models.CharField(
        _("Серийный номер"),
        max_length=100,
    )

    name = models.CharField(
        _("Название модуля"),
        max_length=255,
        blank=False,
        null=False,
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submodules",
        verbose_name=_("Родительский модуль"),
    )

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        verbose_name=_("Производитель"),
    )

    version = models.CharField(
        _("Версия"),
        max_length=50,
    )

    description = models.TextField(_("Описание"), null=True, blank=True)

    class ModuleStatus(models.TextChoices):
        """Enumeration of possible module statuses."""

        IN_PROGRESS = "in_progress", _("В разработке")
        COMPLETED = "completed", _("Завершен")
        CANCELLED = "cancelled", _("Отменен")

    module_status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=ModuleStatus.choices,
        default=ModuleStatus.IN_PROGRESS,
    )

    def __str__(self) -> str:
        """Return string representation of the module including name and serial number."""  # noqa: E501
        return f"{self.name or 'Без названия'} (S/N: {self.serial or 'нет'})"

    class Meta:
        """Model metadata: database table name, ordering, verbose names and indexes."""

        db_table: ClassVar[str] = "modules"
        ordering: ClassVar[list[str]] = ["-updated_on"]
        verbose_name: ClassVar[str] = _("Модуль")
        verbose_name_plural: ClassVar[str] = _("Модули")
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["serial"]),
            models.Index(fields=["part_number"]),
            models.Index(fields=["name"]),
            models.Index(fields=["machine", "serial"]),
        ]
