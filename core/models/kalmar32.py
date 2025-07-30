"""Kalmar32 model for equipment specification and management.

Includes registration, certification, components, and validation logic.
"""
from datetime import date
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator, URLValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.validators import validate_serial_number_format, validate_weight_positive

CALIBRATION_EXPIRE_DAYS: ClassVar[int] = 365


class Kalmar32(models.Model):
    """Kalmar32 model with full equipment specification.

    Attributes:
        serial_number (str): Unique equipment serial number.
        shipment_date (date): Equipment shipment date.
        case_number (str): Storage case number.
        calibration_certificate (Optional[str]): Calibration certificate number.
        calibration_date (Optional[date]): Last calibration date.
        weight (Optional[float]): Weight with packaging in kg.

    """

    # Регистрационные данные
    serial_number = models.CharField(
        _("Серийный номер"),
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(1),
            MaxLengthValidator(50),
            validate_serial_number_format,
        ],
        help_text=_("Уникальный серийный номер оборудования"),
    )
    shipment_date = models.DateField(
        _("Дата отгрузки"),
        default=date.today,
        help_text=_("Дата отгрузки оборудования со склада"),
    )
    case_number = models.CharField(
        _("Номер кейса"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Номер кейса для хранения оборудования"),
    )

    # Основные компоненты
    first_phased_array_converters = models.CharField(
        _("Преобразователи РА2.25L16 1.1х10-17"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("S/n первого преобразователя на фазированной решетке"),
    )

    second_phased_array_converters = models.CharField(
        _("Преобразователи РА2.25L16 1.1х10-17"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("S/n второго преобразователя на фазированной решетке"),
    )
    battery_case = models.CharField(
        _("Корпус АКБ"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Серийный номер корпуса аккумулятора"),
    )

    # Блоки и модули
    aos_block = models.CharField(
        _("Блок AOS"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Номер блока AOS (распределительная коробка и коробка энкодеров)"),
    )
    flash_drive = models.CharField(
        _("Флеш-накопитель с ПО"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Наличие флеш-накопителя с ПО 'Кальмар 32+'"),
    )
    co3r_measure = models.CharField(
        _("Мера СО-3Р"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Номер меры СО-3Р"),
    )

    # Сертификация и проверки
    calibration_certificate = models.CharField(
        _("Сертификат калибровки"),
        max_length=100,
        blank=True,
        validators=[MaxLengthValidator(100)],
        help_text=_("Номер сертификата калибровки"),
    )
    calibration_date = models.DateField(
        _("Дата калибровки"),
        null=True,
        blank=True,
        help_text=_("Дата последней калибровки оборудования"),
    )

    # ЗИП (комплект запасных частей)
    has_tablet_screws = models.BooleanField(
        _("Винты для планшета"),
        default=False,
        help_text=_("Наличие винтов 4х8мм для крепления планшета (4 шт)"),
    )
    has_ethernet_cable = models.BooleanField(
        _("Интернет кабель"),
        default=False,
        help_text=_("Наличие патч-корда 0.5м, 100Мбит/сек"),
    )
    battery_charger = models.CharField(
        _("Сетевая зарядка аккумулятора"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Номер сетевой зарядки аккумулятора"),
    )
    tablet_charger = models.CharField(
        _("Зарядка планшета"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Номер зарядки для планшета"),
    )
    has_tool_kit = models.BooleanField(
        _("Набор инструментов"),
        default=False,
        help_text=_(
            "Наличие набора инструментов (сумка, шестигранники, отвертка, пассатижи)",
        ),
    )

    # Проверка и документирование
    software_check = models.CharField(
        _("Проверка ПО"),
        max_length=200,
        blank=True,
        validators=[MaxLengthValidator(200)],
        help_text=_("Результаты проверки работоспособности ПО"),
    )
    photo_video_url = models.URLField(
        _("Фото, видео"),
        blank=True,
        validators=[URLValidator()],
        help_text=_("URL фотографии. видео преобразователей"),
    )
    weight = models.FloatField(
        _("Вес с упаковкой"),
        null=True,
        blank=True,
        validators=[validate_weight_positive],
        help_text=_("Вес оборудования с упаковкой в килограммах"),
    )
    notes = models.TextField(
        _("Примечания"),
        blank=True,
        help_text=_("Дополнительные заметки по оборудованию"),
    )

    # Дополнительные компоненты
    manual_inclined = models.CharField(
        _("Ручной наклонный преобразователь"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Номер ручного наклонного РА2.25L16 0.9х10-17"),
    )
    straight = models.CharField(
        _("Прямой преобразователь"),
        max_length=50,
        blank=True,
        validators=[MaxLengthValidator(50)],
        help_text=_("Номер прямого 0° РА5.0L16 0.6х10-17"),
    )
    photo_url = models.URLField(
        _("Фото"),
        blank=True,
        validators=[URLValidator()],
        help_text=_("URL фото оборудования"),
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
        return f"{self.serial_number} ({self.shipment_date})"

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
        self._validate_calibration_dates()

    def _validate_calibration_dates(self) -> None:
        """Validate consistency of calibration and shipment dates."""
        if self.calibration_date and self.calibration_date > timezone.now().date():
                raise ValidationError(
                    _("Дата калибровки не может быть в будущем"),
                )
