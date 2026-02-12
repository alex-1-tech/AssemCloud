"""Phasar32 model for equipment specification and management.

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


class Phasar32(models.Model):
    """Phasar32 model with equipment specification."""

    # Регистрационные данные
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
        related_name="phasar32_license",
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

    personalised_name_tag = models.CharField(
        _("Персонализированная бирка"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Personalised name tag"),
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

    # Ultrasonic phased array PULSAR OEM 16/128
    ultrasonic_phased_array_pulsar = models.CharField(
        _("Ультразвуковая фазированная решетка PULSAR OEM 16/128"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Ultrasonic phased array PULSAR OEM 16/128 established"),
    )

    dcn = models.CharField(
        _("Блок 0° ФР"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("DCN P112-2,5-F"),
    )

    ab_back = models.CharField(
        _("Отъезжающий  блок ФР ( преобразователь одинарный)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("AB-back PA2,5L16 1,1x10-17-F"),
    )

    gf_combo = models.CharField(
        _(
            "блок ФР контроля рабочей грани головки рельса "
            "( преобразовать комбинированный )"
        ),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("GF combo 2PA2,5L16 0,6x10-10-F"),
    )

    ff_combo = models.CharField(
        _(
            "блок ФР контроля нерабочей грани головки рельса "
            "( преобразовать комбинированный )"
        ),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("FF combo 2PA2,5L16 0,6x10-10-F"),
    )

    ab_front = models.CharField(
        _("Наезжающий  блок ФР ( преобразователь одинарный)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("AB-front PA2,5L16 1,1x10-17-F"),
    )

    flange_50 = models.CharField(
        _("низкочастотный блок контроля перьев подошвы рельса"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Flange 50 P112-0,6-50-F"),
    )

    manual_probs = models.CharField(
        _("Ручной наклонный ( отдельный преобразователь )"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Manual probs PA2.25L16 0.9x10-17"),
    )

    has_dc_cable_battery = models.BooleanField(
        _("Dc cable кабель"),
        default=False,
        help_text=_("Dc cable battery"),
    )

    has_ethernet_cables = models.BooleanField(
        _("Ethernet кабель"),
        default=False,
        help_text=_("Ethernet cables"),
    )

    water_tank_with_tap = models.CharField(
        _("Резервуар для воды с краном"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Water tank with a tap"),
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
        _("Пароль для виндоус"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Windows password"),
    )

    # Дополнительные поля
    notes = models.TextField(
        _("Примечания"),
        blank=True,
        help_text=_("Дополнительные заметки по оборудованию"),
    )

    class Meta:
        """Meta options for Phasar32 model."""

        verbose_name = _("Фазар32")
        verbose_name_plural = _("Фазары32")
        ordering: ClassVar[list[str]] = ["-shipment_date", "serial_number"]
        constraints: ClassVar[list] = [
            models.UniqueConstraint(
                fields=["serial_number"],
                name="unique_phasar32_serial_number",
                violation_error_message=_(
                    "Фазар32 с таким серийным номером уже существует",
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
        """URL for detailed view of Phasar32."""
        return reverse("phasar32:detail", kwargs={"pk": self.pk})

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
