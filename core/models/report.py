"""Report model for equipment documentation and analysis results.

Includes report generation, measurement data storage, and file management logic.
Stores JSON/PDF reports and rail measurement records with timestamp-based organization.
"""
from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import Kalmar32, Phasar01, Phasar02


def _generate_timestamped_path(
    instance: Report, filename: str, subfolder: str
) -> str:
    """Generate timestamp-based upload path for report files."""
    if instance.kalmar32:
        equipment_type = "kalmar32"
        serial_number = instance.kalmar32.serial_number
    elif instance.phasar01:
        equipment_type = "phasar01"
        serial_number = instance.phasar01.serial_number
    elif instance.phasar02:
        equipment_type = "phasar02"
        serial_number = instance.phasar02.serial_number
    else:
        equipment_type = "unknown"
        serial_number = "unknown"

    path_date = instance.report_date.strftime("%Y-%m-%d/")
    path = f"reports/{equipment_type}/{serial_number}"
    path += f"/{instance.number_to}/{path_date}"
    path += f"/{subfolder}/{filename}"
    return path


def report_json_upload_to(instance: Report, filename: str) -> str:  # noqa: ARG001
    """Upload path for JSON reports."""
    return _generate_timestamped_path(instance, "report.json", "json")


def report_pdf_upload_to(instance: Report, filename: str) -> str:  # noqa: ARG001
    """Upload path for PDF reports."""
    return _generate_timestamped_path(instance, "report.pdf", "pdf")


def rail_record_before_upload_to(instance: Report, filename: str) -> str:  # noqa: ARG001
    """Upload path for 'before' rail records."""
    return _generate_timestamped_path(instance, "rail_record.zip", "before_to")


def rail_record_after_upload_to(instance: Report, filename: str) -> str:  # noqa: ARG001
    """Upload path for 'after' rail records."""
    return _generate_timestamped_path(instance, "rail_record.zip", "after_to")


class Report(models.Model):
    """Report model for equipment documentation.

    Attributes:
        kalmar32: Related Kalmar32 equipment (optional)
        phasar01: Related Phasar01 equipment (optional)
        phasar02: Related Phasar02 equipment (optional)
        report_date: Date of report creation
        json_report: JSON version of report (report.json)
        pdf_report: PDF version of report (report.pdf)
        rail_record_before: Rail measurements before service (before_to/rail_record.zip)
        rail_record_after: Rail measurements after service (after_to/rail_record.zip)

    """

    kalmar32 = models.ForeignKey(
        Kalmar32,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name=_("Оборудование Кальмар32"),
        help_text=_("Связанное оборудование Kalmar32"),
        null=True,
        blank=True,
    )

    phasar01 = models.ForeignKey(
        Phasar01,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name=_("Оборудование Фазар01"),
        help_text=_("Связанное оборудование Phasar01"),
        null=True,
        blank=True,
    )

    phasar02 = models.ForeignKey(
        Phasar02,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name=_("Оборудование Фазар02"),
        help_text=_("Связанное оборудование Phasar02"),
        null=True,
        blank=True,
    )

    report_date = models.DateField(
        _("Дата отчета"),
        default=datetime.now,
        help_text=_("Дата создания отчета"),
    )

    NUMBER_TO_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("TO-1", "TO-1"),
        ("TO-2", "TO-2"),
        ("TO-3", "TO-3"),
    ]
    number_to = models.CharField(
        "Номер проведенного ТО",
        max_length=10,
        choices=NUMBER_TO_CHOICES,
    )

    json_report = models.FileField(
        _("JSON отчет"),
        upload_to=report_json_upload_to,
        help_text=_("Файл отчета в формате JSON (report.json)"),
        blank=True,
    )
    pdf_report = models.FileField(
        _("PDF отчет"),
        upload_to=report_pdf_upload_to,
        help_text=_("Файл отчета в формате PDF (report.pdf)"),
        blank=True,
    )
    rail_record_before = models.FileField(
        _("Запись рельсов (до)"),
        upload_to=rail_record_before_upload_to,
        help_text=_(
            "Архив с записями рельсов до обслуживания (before_to/rail_record.zip)"
        ),
        blank=True,
    )
    rail_record_after = models.FileField(
        _("Запись рельсов (после)"),
        upload_to=rail_record_after_upload_to,
        help_text=_(
            "Архив с записями рельсов после обслуживания (after_to/rail_record.zip)"
        ),
        blank=True,
    )

    class Meta:
        """Meta options for Report model."""

        verbose_name = _("Отчет")
        verbose_name_plural = _("Отчеты")
        ordering: ClassVar[list[str]] = ["-report_date"]
        indexes: ClassVar[list] = [
            models.Index(fields=["report_date"]),
            models.Index(fields=["kalmar32"]),
            models.Index(fields=["phasar01"]),
            models.Index(fields=["phasar02"]),
        ]

    def __str__(self) -> str:
        """Representate string of the report."""
        if self.kalmar32:
            equipment_info = f"Kalmar32 {self.kalmar32.serial_number}"
        elif self.phasar01:
            equipment_info = f"Phasar01 {self.phasar01.serial_number}"
        elif self.phasar02:
            equipment_info = f"Phasar02 {self.phasar02.serial_number}"
        else:
            equipment_info = "Unknown equipment"

        return _("Отчет от {datetime} для {equipment}").format(
            datetime=self.report_date.strftime("%d.%m.%Y"),
            equipment=equipment_info,
        )

    def save(self, *args: object, **kwargs: object) -> None:
        """Override save with validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Additional model validation."""
        super().clean()
        self._validate_dates()
        self._validate_equipment_reference()
        self._validate_unique_constraint()

    def _validate_dates(self) -> None:
        """Ensure dates are valid."""
        now = timezone.now()

        if self.report_date > now.date():
            raise ValidationError(_("Дата отчета не может быть в будущем"))

    def _validate_equipment_reference(self) -> None:
        """Validate that exactly one equipment reference is set."""
        if not self.kalmar32 and not self.phasar01 and not self.phasar02:
            raise ValidationError(
                _("Отчет должен быть привязан либо к Kalmar32, либо к Phasar01")
            )

        if (self.kalmar32 and self.phasar01) or \
            (self.kalmar32 and self.phasar02) or \
                (self.phasar01 and self.phasar02):
            raise ValidationError(
                _("Отчет не может быть одновременно привязан и к Kalmar32 и к Phasar01")
            )

    def _validate_unique_constraint(self) -> None:
        """Validate unique constraint for the equipment, date and TO number."""
        if self.kalmar32:
            queryset = Report.objects.filter(
                kalmar32=self.kalmar32,
                report_date=self.report_date,
                number_to=self.number_to,
            ).exclude(pk=self.pk)

            if queryset.exists():
                raise ValidationError(
                    _(
                        "Отчет для этого Kalmar32 с такой датой и номером ТО "
                        "уже существует"
                    )
                )

        elif self.phasar01:
            queryset = Report.objects.filter(
                phasar=self.phasar01,
                report_date=self.report_date,
                number_to=self.number_to,
            ).exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError(
                    _(
                        "Отчет для этого Phasar01 с такой датой и номером ТО "
                        "уже существует"
                    )
                )
        elif self.phasar02:
            queryset = Report.objects.filter(
                phasar=self.phasar02,
                report_date=self.report_date,
                number_to=self.number_to,
            ).exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError(
                    _(
                        "Отчет для этого Phasar02 с такой датой и номером ТО "
                        "уже существует"
                    )
                )

    @property
    def equipment(self) -> Kalmar32 | Phasar01 | Phasar02:
        """Return the associated equipment instance."""
        return self.kalmar01 or self.phasar01 or  self.phasar02

    @property
    def equipment_type(self) -> str:
        """Return equipment type as string."""
        if self.kalmar32:
            return "kalmar32"
        if self.phasar01:
            return "phasar01"
        if self.phasar02:
            return "phasar02"
        return "unknown"

    @property
    def file_structure(self) -> str:
        """Return the expected file storage structure."""
        equipment_type = self.equipment_type
        serial_number = self.equipment.serial_number if self.equipment else "unknown"

        return (
            f"reports/{equipment_type}/{serial_number}/{self.report_date.strftime('%Y-%m-%d/')}/\n"
            f"  json/report.json\n"
            f"  pdf/report.pdf\n"
            f"  before_to/rail_record.zip\n"
            f"  after_to/rail_record.zip"
        )
