"""Models for storing information about modules and their attributes.

This module defines the `Module` model, which represents components of a machine.
It includes technical and manufacturing information such as blueprint files (PDF, STEP),
part number, decimal number, version, status, manufacturer.

Key fields:
- machine: Reference to the machine this module belongs to.
- decimal: Decimal (decimal/part) number of the module.
- name: Name of the module.
=- manufacturer: Optional reference to the manufacturer.
- version: Version string.
- description: Optional text description.
- scheme_file: PDF blueprint file.
- step_file: STEP 3D model file for CAD systems.
- module_status: Status of the module (in progress, completed, cancelled).
"""

from typing import ClassVar

from django.core.validators import FileExtensionValidator
from mptt.models import MPTTModel, TreeForeignKey

from core.models import Machine, Manufacturer
from core.models.base import (
    NormalizeMixin,
    ReprMixin,
    TimeStampedModelWithUser,
    _,
    models,
)


class Module(ReprMixin, NormalizeMixin, TimeStampedModelWithUser):
    """Model representing a machine module with various attributes.

    Modules can represent standalone or nested components within machines,
    with references to manufacturers and hierarchical relationships.

    The model supports hierarchical module structures, links to manufacturers,
    and stores both 2D and 3D blueprint files for each module.
    """

    decimal = models.CharField(
        _("Децимальный номер"),
        max_length=100,
    )

    name = models.CharField(
        _("Название модуля"),
        max_length=30,
        blank=False,
        null=False,
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
        """Return string representation of the module including name and decimal number."""  # noqa: E501
        return f"{self.name or 'Без названия'} (S/N: {self.decimal or 'нет'})"

    class Meta:
        """Мета-данные для Module."""

        db_table: ClassVar[str] = "modules"
        ordering: ClassVar[list[str]] = ["-updated_on"]
        verbose_name: ClassVar[str] = _("Модуль")
        verbose_name_plural: ClassVar[str] = _("Модули")
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["decimal"]),
            models.Index(fields=["name"]),
        ]


class MachineModule(ReprMixin, MPTTModel):
    """Intermediary model linking modules to machines with metadata.

    This model enables a many-to-many relationship between `Module` and `Machine`
    and supports additional fields like comments and creation date.
    """

    module_link = models.ForeignKey(
        Module,
        on_delete=models.RESTRICT,
        verbose_name=_("Модуль (справочник)"),
        related_name="machine_modules_links",
    )

    module = TreeForeignKey(
        "self",
        on_delete=models.RESTRICT,
        related_name="children_modules",
        verbose_name=_("Модуль"),
    )

    parent_module_link = models.ForeignKey(
        Module,
        on_delete=models.RESTRICT,
        verbose_name=_("Родительский модуль (справочник)"),
        null=True,
        blank=True,
        related_name="parent_module_links",
    )

    parent_module = TreeForeignKey(
        "self",
        on_delete=models.RESTRICT,
        verbose_name=_("Родительский модуль"),
        null=True,
        blank=True,
        related_name="parent_modules",
    )

    machine = models.ForeignKey(
        Machine,
        on_delete=models.RESTRICT,
        verbose_name=_("Машина"),
        help_text="Reference to the machine in the association.",
        related_name="module_machines_links",
    )

    quantity = models.PositiveIntegerField(
        _("Количество"),
        default=1,
    )

    def __str__(self) -> str:
        """Return a string showing the module-machine association."""
        return f"{self.machine}:\
             {self.parent_module_link} <-> {self.module_link} (x{self.quantity})"

    class MPTTMeta:
        """MPTT metadata for hierarchical structure."""

        order_insertion_by: ClassVar[list[str]] = ["module_link__decimal"]

    class Meta:
        """Model metadata: database table name, verbose names and unique constraint."""

        db_table: ClassVar[str] = "module_machines"
        ordering: ClassVar[list[str]] = ["tree_id", "id"]
        verbose_name: ClassVar[str] = _("Связь Модуль-Машина")
        verbose_name_plural: ClassVar[str] = _("Связи Модуль-Машина")
        unique_together: ClassVar[tuple[str, str]] = ("module", "machine")
        constraints: ClassVar[list[models.constraints.BaseConstraint]] = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="quantity_module_machine_positive",
            ),
            models.UniqueConstraint(
                fields=["module_link", "parent_module"],
                name="unique_parent_module_module",
            ),
        ]
