from __future__ import annotations
from datetime import date
from typing import ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _


class EquipmentType(models.Model):
    name = models.CharField(
        _("Internal name"),
        max_length=50,
        unique=True,
        help_text=_("Unique identifier"),
    )
    title = models.CharField(
        _("Display name"),
        max_length=100,
        help_text=_("Display name"),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Equipment description"),
    )
    installer_path = models.CharField(
        _("Installer filename"),
        max_length=100,
        blank=True,
        help_text=_("Installer file name"),
    )
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Equipment type")
        verbose_name_plural = _("Equipment types")
        ordering = ["name"]

    def __str__(self):
        return self.title or self.name


class RailType(models.TextChoices):
    UIC60 = "UIC60", _("UIC 60")
    IRS52 = "IRS52", _("IRS 52")
    R65 = "R65", _("R65")
    NONE = "NONE", _("None")


class Model(models.Model):
    """Specific variant of a model (e.g. Kalmar32 + UIC60 + Ver2 Plant)."""

    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.PROTECT,
        related_name="variants",
        verbose_name=_("Equipment type"),
        null=True,
    )
    version = models.CharField(
        _("Model version"),
        max_length=50,
        help_text=_("Hardware/Plant version, e.g. Ver_1, Ver2 Plant"),
    )
    type_rail = models.CharField(
        _("Rail type"),
        max_length=10,
        choices=RailType.choices,
        default=RailType.NONE,
    )
    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["equipment_type", "version", "type_rail"],
                name="unique_model_variant",
            ),
        ]

    def __str__(self):
        rail = f" ({self.get_type_rail_display()})" if self.type_rail != RailType.NONE else ""
        return f"{self.equipment_type.title} | {self.version}{rail}"


class SchemeQuerySet(models.QuerySet):
    def for_model(
        self, model_id: int | None = None, model_instance: Model | None = None
    ) -> SchemeQuerySet:
        """Схемы, привязанные к тому же базовому model_name, что и у переданного Model."""
        if model_instance is None:
            if not model_id:
                return self.none()
            model_instance = Model.objects.filter(id=model_id).only("equipment_type").first()
            if model_instance is None:
                return self.none()
        return self.filter(equipment_type=model_instance.equipment_type)


class Scheme(models.Model):
    """Dynamic fields schema bound ONLY to base model name."""

    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.PROTECT,
        related_name="schemes",
        verbose_name=_("Equipment type"),
        null=True,
    )
    version = models.PositiveIntegerField(
        _("Scheme version"),
        help_text=_("Sequential scheme layout version"),
    )
    fields_description = models.JSONField(
        _("Fields description"),
        default=dict,
    )
    is_latest = models.BooleanField(
        _("Is latest scheme"),
        default=False,
    )
    objects = SchemeQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["equipment_type", "version"],
                name="unique_scheme_version_per_type",
            ),
        ]

    def __str__(self):
        return f"Scheme v{self.version} for {self.equipment_type.title}"


class Equipment(models.Model):
    """Equipment unit instance."""

    model = models.ForeignKey(
        Model,
        on_delete=models.PROTECT,
        related_name="equipment_items",
        verbose_name=_("Model Variant"),
    )
    scheme = models.ForeignKey(
        Scheme,
        on_delete=models.PROTECT,
        related_name="equipment_items",
        verbose_name=_("Fields Scheme"),
    )
    license = models.OneToOneField(
        "License",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipment",
    )
    serial_number = models.CharField(
        _("Serial number"),
        max_length=50,
        unique=True,
        db_index=True,
    )
    invoice = models.CharField(_("Invoice"), max_length=100, blank=True)
    packet_list = models.CharField(_("Packet list"), max_length=100, blank=True)
    shipment_date = models.DateField(_("Shipment date"), null=True, blank=True, default=date.today)

    other_data = models.JSONField(_("Dynamic data"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Equipment")
        verbose_name_plural = _("Equipment items")

    def __str__(self) -> str:
        return f"s/n: {self.serial_number} ({self.model})"
