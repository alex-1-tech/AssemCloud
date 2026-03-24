"""Phasar02 model for equipment specification and management.

Dual version with left and right channels for rail double-stranded phased arrays.
"""

from datetime import date
from typing import ClassVar

from decouple import config
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Phasar02(models.Model):
    """Phasar02 model with equipment specification (dual version)."""

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
        related_name="phasar02_license",
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

    ultrasonic_phased_array_pulsar_left = models.CharField(
        _("Ультразвуковая фазированная решетка PULSAR OEM 16/128 (ЛЕВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Ultrasonic phased array PULSAR OEM 16/128 established (LEFT)"),
    )

    dcn_left = models.CharField(
        _("Блок 0° ФР (ЛЕВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("DCN P112-2,5-F (LEFT)"),
    )

    ab_back_left = models.CharField(
        _("Отъезжающий блок ФР (ЛЕВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("AB-back PA2,5L16 1,1x10-17-F (LEFT)"),
    )

    gf_combo_left = models.CharField(
        _("Блок ФР рабочей грани (ЛЕВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("GF combo 2PA2,5L16 0,6x10-10-F (LEFT)"),
    )

    ff_combo_left = models.CharField(
        _("Блок ФР нерабочей грани (ЛЕВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("FF combo 2PA2,5L16 0,6x10-10-F (LEFT)"),
    )

    ab_front_left = models.CharField(
        _("Наезжающий блок ФР (ЛЕВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("AB-front PA2,5L16 1,1x10-17-F (LEFT)"),
    )

    flange_50_left = models.CharField(
        _("Низкочастотный блок подошвы (ЛЕВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Flange 50 P112-0,6-50-F (LEFT)"),
    )

    manual_probs_left = models.CharField(
        _("Ручной наклонный преобразователь (ЛЕВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Manual probs PA2.25L16 0.9x10-17 (LEFT)"),
    )

    has_dc_cable_battery_left = models.BooleanField(
        _("DC кабель от батареи (ЛЕВЫЙ)"),
        default=False,
        help_text=_("DC Cable from Battery (LEFT)"),
    )

    has_ethernet_cables_left = models.BooleanField(
        _("Ethernet кабель (ЛЕВЫЙ)"),
        default=False,
        help_text=_("Ethernet Cables (LEFT)"),
    )

    ultrasonic_phased_array_pulsar_right = models.CharField(
        _("Ультразвуковая фазированная решетка PULSAR OEM 16/128 (ПРАВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Ultrasonic phased array PULSAR OEM 16/128 established (RIGHT)"),
    )

    dcn_right = models.CharField(
        _("Блок 0° ФР (ПРАВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("DCN P112-2,5-F (RIGHT)"),
    )

    ab_back_right = models.CharField(
        _("Отъезжающий блок ФР (ПРАВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("AB-back PA2,5L16 1,1x10-17-F (RIGHT)"),
    )

    gf_combo_right = models.CharField(
        _("Блок ФР рабочей грани (ПРАВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("GF combo 2PA2,5L16 0,6x10-10-F (RIGHT)"),
    )

    ff_combo_right = models.CharField(
        _("Блок ФР нерабочей грани (ПРАВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("FF combo 2PA2,5L16 0,6x10-10-F (RIGHT)"),
    )

    ab_front_right = models.CharField(
        _("Наезжающий блок ФР (ПРАВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("AB-front PA2,5L16 1,1x10-17-F (RIGHT)"),
    )

    flange_50_right = models.CharField(
        _("Низкочастотный блок подошвы (ПРАВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Flange 50 P112-0,6-50-F (RIGHT)"),
    )

    manual_probs_right = models.CharField(
        _("Ручной наклонный преобразователь (ПРАВЫЙ)"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Manual probs PA2.25L16 0.9x10-17 (RIGHT)"),
    )

    has_dc_cable_battery_right = models.BooleanField(
        _("DC кабель от батареи (ПРАВЫЙ)"),
        default=False,
        help_text=_("DC Cable from Battery (RIGHT)"),
    )

    has_ethernet_cables_right = models.BooleanField(
        _("Ethernet кабель (ПРАВЫЙ)"),
        default=False,
        help_text=_("Ethernet Cables (RIGHT)"),
    )

    water_tank_with_tap = models.CharField(
        _("Резервуар для воды с краном"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Water tank with a tap"),
    )


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


    wifi_router_address = models.CharField(
        _("Адрес Wi-Fi роутера"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("WiFi router address"),
    )

    windows_password = models.CharField(
        _("Пароль для Windows"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Windows password"),
    )

    notes = models.TextField(
        _("Примечания"),
        blank=True,
        help_text=_("Дополнительные заметки по оборудованию"),
    )

    class Meta:
        """Meta options for Phasar02 model."""

        verbose_name = _("Фазар02")
        verbose_name_plural = _("Фазары02")
        ordering: ClassVar[list[str]] = ["-shipment_date", "serial_number"]
        constraints: ClassVar[list] = [
            models.UniqueConstraint(
                fields=["serial_number"],
                name="unique_phasar02_serial_number",
                violation_error_message=_(
                    "Фазар02 с таким серийным номером уже существует",
                ),
            ),
        ]

    def __str__(self) -> str:
        """Return string representation of the object."""
        return f"Phasar02 s/n: {self.serial_number}"

    def save(self, *args: object, **kwargs: object) -> None:
        """Override save with additional processing."""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """URL for detailed view of Phasar02."""
        return reverse("phasar02:detail", kwargs={"pk": self.pk})

    def clean(self) -> None:
        """Additional model validation."""
        super().clean()
