"""Admin configuration for Kalmar32 equipment."""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Kalmar32


@admin.register(Kalmar32)
class Kalmar32Admin(admin.ModelAdmin):
    """Admin configuration for managing Kalmar32 equipment."""

    list_display = (
        "serial_number",
        "shipment_date",
        "case_number",
    )
    list_filter = (
        "shipment_date",
        "calibration_date",
        "has_tablet_screws",
        "has_ethernet_cable",
        "has_tool_kit",
    )
    search_fields = (
        "serial_number",
        "case_number",
        "calibration_certificate",
        "first_phased_array_converters",
        "second_phased_array_converters",
        "battery_case",
        "aos_block",
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
            _("Основные компоненты"),
            {
                "fields": (
                    "first_phased_array_converters",
                    "second_phased_array_converters",
                    "battery_case",
                ),
            },
        ),
        (
            _("Блоки и модули"),
            {
                "fields": (
                    "aos_block",
                    "flash_drive",
                    "co3r_measure",
                ),
            },
        ),
        (
            _("Сертификация"),
            {
                "fields": (
                    "calibration_certificate",
                    "calibration_date",
                ),
            },
        ),
        (
            _("Комплект ЗИП"),
            {
                "fields": (
                    "has_tablet_screws",
                    "has_ethernet_cable",
                    "battery_charger",
                    "tablet_charger",
                    "has_tool_kit",
                ),
            },
        ),
        (
            _("Дополнительные компоненты"),
            {
                "fields": (
                    "manual_inclined",
                    "straight",
                    "photo_video_url"
                ),
            },
        ),
        (
            _("Проверка и документирование"),
            {
                "fields": (
                    "software_check",
                    "weight",
                    "photo_url",
                    "notes",
                ),
            },
        ),
    )

    @admin.display(description=_("Фото"))
    def display_photo(self, obj: Kalmar32) -> str:
        """Return an HTML image link if photo_url exists, otherwise return '-'."""
        if obj.photo_url:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="object-fit: cover;"/></a>',  # noqa: E501
                obj.photo_url,
                obj.photo_url,
            )
        return "-"

