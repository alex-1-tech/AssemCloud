"""Models for storing information about parts and their relationships to modules.

This module contains the Part and ModulePart models, which describe
parts, their characteristics, and relationships to modules, including the number
of each part in a particular module.
"""

from typing import ClassVar

from core.models import Manufacturer, Module
from core.models.base import (
    NormalizeMixin,
    ReprMixin,
    TimeStampedModelWithUser,
    _,
    models,
)


class Part(ReprMixin, NormalizeMixin, TimeStampedModelWithUser):
    """Model representing a part and its manufacturing details.

    This model describes an individual part used across various modules,
    including all necessary information about its manufacturing process
    such as manufacturer, manufacture date, material, and description.

    It is used together with the ModulePart model to define the quantity
    and placement of parts within modules.
    """

    name = models.CharField(
        _("Название"),
        max_length=255,
        null=False,
        blank=False,
    )

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parts_manufactured",
        verbose_name=_("Производители"),
    )

    description = models.TextField(_("Описание детали"), blank=True, null=True)

    material = models.CharField(_("Материал"), max_length=100, blank=True)

    manufacture_date = models.DateField(_("Дата производства"), blank=True, null=True)

    def __str__(self) -> str:
        """Return the name of the part."""
        return self.name

    class Meta:
        """Model metadata: database table name, verbose names, ordering and indexes."""

        db_table: ClassVar[str] = "parts"
        verbose_name: ClassVar[str] = _("Деталь")
        verbose_name_plural: ClassVar[str] = _("Детали")
        ordering: ClassVar[list[str]] = ["name"]
        indexes: ClassVar[list[models.Index]] = [
            # Index to optimize filtering by manufacture date
            models.Index(fields=["manufacture_date"]),
        ]


class ModulePart(ReprMixin, models.Model):
    """Model linking parts to modules with quantity information.

    Represents the association between a part and a module,
    specifying how many of each part are used in a given module.
    """

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="module_parts",
        verbose_name=_("Модуль"),
    )

    part = models.ForeignKey(
        Part,
        on_delete=models.RESTRICT,
        related_name="part_modules",
        verbose_name=_("Деталь"),
    )

    quantity = models.PositiveIntegerField(
        _("Количество"),
        default=1,
        help_text=_("Number of parts in the module"),
    )

    def __str__(self) -> str:
        """Return a string representation of the module-part relation with quantity."""
        return f"{self.module} × {self.part} ({self.quantity})"  # noqa: RUF001

    class Meta:
        """Model metadata: database table name, verbose names and constraints."""

        db_table: ClassVar[str] = "module_part"
        verbose_name: ClassVar[str] = _("Связь Деталь-Модуль")
        verbose_name_plural: ClassVar[str] = _("Связи Деталь-Модуль")
        constraints: ClassVar[list[models.constraints.BaseConstraint]] = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="quantity_positive",
            ),
            models.UniqueConstraint(
                fields=["module", "part"],
                name="unique_module_part",
            ),
        ]
