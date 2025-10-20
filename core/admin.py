"""Admin configuration for Kalmar32 equipment."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Kalmar32, Report


@admin.register(Kalmar32)
class Kalmar32Admin(admin.ModelAdmin):
    """Admin configuration for managing Kalmar32 equipment."""

    list_display = (
        "serial_number",
        "shipment_date",
        "software_installer_link",
    )
    list_filter = (
        "shipment_date",
        "has_dc_cable_battery",
        "has_ethernet_cables",
        "has_repair_tool_bag",
        "has_installed_nameplate",
    )
    search_fields = (
        "serial_number",
        "pc_tablet_dell_7230",
        "ultrasonic_phased_array_pulsar",
        "manual_probs_36",
        "straight_probs_0",
        "dc_battery_box",
        "calibration_block_so_3r",
    )
    date_hierarchy = "shipment_date"
    ordering = ("-shipment_date",)
    fieldsets = (
        (
            _("Регистрационные данные"),
            {
                "fields": (
                    "serial_number",
                    "shipment_date",
                    "case_number",
                ),
            },
        ),
        (
            _("Планшет Dell 7230"),
            {
                "fields": (
                    "pc_tablet_dell_7230",
                    "software_installer_link",
                    "ac_dc_power_adapter_dell",
                    "dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Ультразвуковая фазированная решетка PULSAR OEM 16/64"),
            {
                "fields": (
                    "ultrasonic_phased_array_pulsar",
                    "manual_probs_36",
                    "straight_probs_0",
                    "has_dc_cable_battery",
                    "has_ethernet_cables",
                ),
            },
        ),
        (
            _("Батарейный блок"),
            {
                "fields": (
                    "dc_battery_box",
                    "ac_dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Калибровка и инструменты"),
            {
                "fields": (
                    "calibration_block_so_3r",
                    "has_repair_tool_bag",
                    "has_installed_nameplate",
                ),
            },
        ),
        (
            _("Дополнительная информация"),
            {
                "fields": ("notes",),
            },
        ),
    )



@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for managing Kalmar32 reports."""

    list_display = (
        "report_date",
        "kalmar",
        "number_to",
        "download_pdf",
        "download_json",
    )
    list_filter = ("report_date",)
    search_fields = (
        "kalmar__serial_number",
        "kalmar__case_number",
    )
    date_hierarchy = "report_date"
    ordering = ("-report_date",)

    fieldsets = (
        (
            _("Общие сведения"),
            {
                "fields": (
                    "kalmar",
                    "report_date",
                    "number_to",
                ),
            },
        ),
        (
            _("Файлы отчета"),
            {
                "fields": (
                    "json_report",
                    "pdf_report",
                ),
            },
        ),
        (
            _("Записи рельсов"),
            {
                "fields": (
                    "rail_record_before",
                    "rail_record_after",
                ),
            },
        ),
    )

    @admin.display(description=_("Скачать PDF"))
    def download_pdf(self, obj: Report) -> str:
        """Provide a download link for the PDF report."""
        if obj.pdf_report:
            return format_html(
                '<a href="{}" target="_blank">📄 PDF</a>',
                obj.pdf_report.url,
            )
        return "-"

    @admin.display(description=_("Скачать JSON"))
    def download_json(self, obj: Report) -> str:
        """Provide a download link for the JSON report."""
        if obj.json_report:
            return format_html(
                '<a href="{}" target="_blank">🗂 JSON</a>',
                obj.json_report.url,
            )
        return "-"
