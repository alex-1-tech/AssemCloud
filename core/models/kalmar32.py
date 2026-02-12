"""Kalmar32 model for equipment specification and management.

Includes registration, components, and validation logic.
"""

from datetime import date
from typing import ClassVar

from decouple import config
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Kalmar32(models.Model):
    """Kalmar32 model with equipment specification."""

    serial_number = models.CharField(
        _("Серийный номер"),
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(1),
            MaxLengthValidator(50),
        ],
        help_text=_("Уникальный серийный номер оборудования"),
    )

    license = models.OneToOneField(
        "License",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kalmar32_license",
        verbose_name=_("Лицензия"),
        help_text=_("Лицензия для этого оборудования"),
    )

    license_password = models.CharField(
        _("License password"),
        max_length=100,
        default=config("LICENSE_DEFAULT_PASSWORD", cast=str),
        help_text=_("Пароль для активации лицензии"),
    )

    shipment_date = models.DateField(
        _("Дата отгрузки"),
        default=date.today,
        help_text=_("Дата отгрузки оборудования со склада"),
    )

    invoice = models.CharField(
        _("Invoice"),
        max_length=100,
        blank=True,
        help_text=_("Invoice number"),
    )

    packet_list = models.CharField(
        _("Packet list"),
        max_length=100,
        blank=True,
        help_text=_("Document number"),
    )

    # PC tablet Latitude Dell 7230
    pc_tablet_dell_7230 = models.CharField(
        _("Планшет Dell 7230"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("PC tablet Latitude Dell 7230"),
    )

    ac_dc_power_adapter_dell = models.CharField(
        _("AC/DC адаптер питания для Dell 7230"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("AC/DC Power adapter for Dell 7230"),
    )

    dc_charger_adapter_battery = models.CharField(
        _("DC адаптер зарядки от батареи для Dell 7230"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("DC Charger adapter for Dell 7230 from battery"),
    )

    # Ultrasonic phased array PULSAR OEM 16/64
    ultrasonic_phased_array_pulsar = models.CharField(
        _("Ультразвуковая фазированная решетка PULSAR OEM 16/64"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Ultrasonic phased array PULSAR OEM 16/64 established"),
    )

    left_probs = models.CharField(
        _("Левый преобразователь"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Left probs PA2.25L16 1.1x10-17"),
    )

    right_probs = models.CharField(
        _("Правый преобразователь"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Right probs PA2.25L16 1.1x10-17"),
    )

    manual_probs = models.CharField(
        _("Ручной преобразователь"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Manual probs PA2.25L16 0.9x10-17"),
    )

    straight_probs = models.CharField(
        _("Прямой преобразователь"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Straight probs PA5.0L16 0.6x10-12"),
    )

    has_dc_cable_battery = models.BooleanField(
        _("DC кабель от батарейного блока"),
        default=False,
        help_text=_("DC Cable from battery box"),
    )

    has_ethernet_cables = models.BooleanField(
        _("Ethernet кабель"),
        default=False,
        help_text=_("Ethernet cables"),
    )

    # DC Battery box
    dc_battery_box = models.CharField(
        _("Батарейный блок DC"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("DC Battery box established"),
    )

    has_ac_dc_charger_adapter_battery = models.BooleanField(
        _("AC/DC адаптер зарядки для батареи"),
        default=False,
        help_text=_("AC/DC Charger adapter for battery"),
    )

    # Calibration and tools
    calibration_block_so_3r = models.CharField(
        _("Калибровочный блок SO-3R"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Calibration bloc SO-3R"),
    )

    has_repair_tool_bag = models.BooleanField(
        _("Ремонтный инструмент с сумкой"),
        default=False,
        help_text=_("Small repair tool with bag"),
    )

    has_installed_nameplate = models.BooleanField(
        _("Установленная табличка с серийным номером"),
        default=False,
        help_text=_("Installed nameplate with serial number"),
    )

    # network settings
    wifi_router_address = models.CharField(
        _("Адресс вай-фай роутера"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("WiFi router address"),
    )

    windows_password = models.CharField(
        _("Пароль Windows"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Пароль учетной записи Windows"),
    )

    # Дополнительные поля
    notes = models.TextField(
        _("Примечания"),
        blank=True,
        help_text=_("Дополнительные заметки по оборудованию"),
    )

    class Meta:
        """Meta options for Kalmar32 model."""

        verbose_name = _("Кальмар32")
        verbose_name_plural = _("Кальмары32")
        ordering: ClassVar[list[str]] = ["-shipment_date", "serial_number"]
        constraints: ClassVar[list] = [
            models.UniqueConstraint(
                fields=["serial_number"],
                name="unique_serial_number",
                violation_error_message=_(
                    "Кальмар32 с таким серийным номером уже существует",
                ),
            ),
        ]

    def __str__(self) -> str:
        """Return string representation of the object."""
        return f"s/n: {self.serial_number}"

    def save(self, *args: object, **kwargs: object) -> None:
        """Override save with additional processing."""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """URL for detailed view of Kalmar32."""
        return reverse("Kalmar32:detail", kwargs={"pk": self.pk})

    def clean(self) -> None:
        """Additional model validation."""
        super().clean()
        self._validate_shipment_date()

    def _validate_shipment_date(self) -> None:
        """Validate shipment date is not in future."""
        if self.shipment_date and self.shipment_date > timezone.now().date():
            raise ValidationError(
                _("Дата отгрузки не может быть в будущем"),
            )
