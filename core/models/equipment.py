from datetime import date
from typing import ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _


class ModelNames(models.TextChoices):
    KALMAR32 = "kalmar32", _("Kalmar 32+")
    PHASARSL = "phasarsl", _("Phasar 01 (SL)")
    PHASARLT = "phasarlt", _("Phasar 01 (LT)")
    PHASARDL = "phasardl", _("Phasar 02 (DL)")
    WIZARD6 = "wizard6", _("Wizard 6")
    WIZARD9 = "wizard8", _("Wizard 8")
    CHAMELEON32 = "chameleon32", _("Chameleon 32+")


class RailType(models.TextChoices):
    UIC60 = "UIC60", _("UIC 60")
    IRS52 = "IRS52", _("IRS 52")
    R65 = "R65", _("R65")
    NONE = "NONE", _("None")


class Model(models.Model):
    """Specific variant of a model (e.g. Kalmar32 + UIC60 + Ver2 Plant)."""

    name = models.CharField(
        _("Model name"),
        max_length=50,
        choices=ModelNames.choices,
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
        verbose_name = _("Model Variant")
        verbose_name_plural = _("Model Variants")
        constraints: ClassVar[list] = [
            models.UniqueConstraint(
                fields=["name", "version", "type_rail"],
                name="unique_model_variant",
            ),
        ]

    def __str__(self) -> str:
        rail = f" ({self.get_type_rail_display()})" if self.type_rail != RailType.NONE else ""
        return f"{self.get_name_display()} | {self.version}{rail}"
class SchemeQuerySet(models.QuerySet):
    def for_model(self, model_id: int | None = None, model_instance: "Model | None" = None) -> "SchemeQuerySet":
        """Схемы, привязанные к тому же базовому model_name, что и у переданного Model."""
        if model_instance is None:
            if not model_id:
                return self.none()
            model_instance = Model.objects.filter(id=model_id).only("name").first()
            if model_instance is None:
                return self.none()
        return self.filter(model_name=model_instance.name)

class Scheme(models.Model):
    """Dynamic fields schema bound ONLY to base model name."""

    model_name = models.CharField(
        _("Model name"),
        max_length=50,
        choices=ModelNames.choices,
        help_text=_("Base model name this scheme belongs to"),
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
        verbose_name = _("Scheme")
        verbose_name_plural = _("Schemes")
        constraints: ClassVar[list] = [
            models.UniqueConstraint(
                fields=["model_name", "version"],
                name="unique_scheme_version_per_model_name",
            ),
        ]

    def __str__(self) -> str:
        return f"Scheme v{self.version} for {self.get_model_name_display()}"


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