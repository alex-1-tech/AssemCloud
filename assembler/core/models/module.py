"""Models for storing information about modules and their attributes.

This module defines the `Module` model, which represents components of a machine.
It includes technical and manufacturing information such as blueprint files (PDF, STEP),
part number, serial number, version, status, manufacturer, and
parent module (for nested module structures).

Key fields:
- machine: Reference to the machine this module belongs to.
- decimal: Decimal (serial/part) number of the module.
- name: Name of the module.
- parent: Optional reference to a parent module (for hierarchy).
- manufacturer: Optional reference to the manufacturer.
- version: Version string.
- description: Optional text description.
- scheme_file: PDF blueprint file.
- step_file: STEP 3D model file for CAD systems.
- module_status: Status of the module (in progress, completed, cancelled).
"""

from typing import ClassVar

from django.core.validators import FileExtensionValidator

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
    with references to manufacturers and hierarchical relationships.

    The model supports hierarchical module structures, links to manufacturers,
    and stores both 2D and 3D blueprint files for each module.
    """

    machine = models.ForeignKey(
        "Machine",
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name=_("Машина"),
        blank=False,
        null=False,
    )

    decimal = models.CharField(
        _("Децимальный номер"),
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

    scheme_file = models.FileField(
        upload_to="blueprints/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name=_("Файл чертежа (PDF)"),
        help_text=_("Загруженный файл чертежа в формате PDF"),
    )

    step_file = models.FileField(
        upload_to="steps/",
        validators=[FileExtensionValidator(allowed_extensions=["step"])],
        verbose_name=_("Файл чертежа (STEP)"),
        help_text=_("3D-модель в формате STEP для CAD-систем"),
    )
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
        return f"{self.name or 'Без названия'} (S/N: {self.decimal or 'нет'})"

    class Meta:
        """Model metadata: database table name, ordering, verbose names and indexes."""

        db_table: ClassVar[str] = "modules"
        ordering: ClassVar[list[str]] = ["-updated_on"]
        verbose_name: ClassVar[str] = _("Модуль")
        verbose_name_plural: ClassVar[str] = _("Модули")
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["decimal"]),
            models.Index(fields=["name"]),
            models.Index(fields=["machine", "decimal"]),
        ]
