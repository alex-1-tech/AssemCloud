"""Admin configuration for Kalmar32, Phasar32, Report, and License models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Kalmar32, License, Phasar32, Report

if TYPE_CHECKING:
    from django.db import models
    from django.db.models import Field
    from django.http import HttpRequest


@admin.register(Kalmar32)
class Kalmar32Admin(admin.ModelAdmin):
    """Admin configuration for managing Kalmar32 equipment."""

    list_display = (
        "serial_number",
        "shipment_date",
        "invoice",
        "license",
    )
    list_filter = (
        "shipment_date",
        "has_dc_cable_battery",
        "has_ethernet_cables",
        "has_repair_tool_bag",
        "has_installed_nameplate",
        "has_ac_dc_charger_adapter_battery",
    )
    search_fields = (
        "serial_number",
        "invoice",
        "packet_list",
        "license__license_key",
        "pc_tablet_dell_7230",
        "ultrasonic_phased_array_pulsar",
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
                    "invoice",
                    "packet_list",
                    "license",
                ),
            },
        ),
        (
            _("Планшет Dell 7230"),
            {
                "fields": (
                    "pc_tablet_dell_7230",
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
                    "left_probs",
                    "right_probs",
                    "manual_probs",
                    "straight_probs",
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
                    "has_ac_dc_charger_adapter_battery",
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
            _("Сетевые настройки"),
            {
                "fields": (
                    "wifi_router_address",
                    "windows_password",
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


@admin.register(Phasar32)
class Phasar32Admin(admin.ModelAdmin):
    """Admin configuration for managing Phasar32 equipment."""

    list_display = (
        "serial_number",
        "shipment_date",
        "invoice",
        "license",
    )
    list_filter = (
        "shipment_date",
        "has_dc_cable_battery",
        "has_ethernet_cables",
        "has_repair_tool_bag",
        "has_installed_nameplate",
        "has_ac_dc_charger_adapter_battery",
    )
    search_fields = (
        "serial_number",
        "invoice",
        "packet_list",
        "license__license_key",
        "pc_tablet_dell_7230",
        "ultrasonic_phased_array_pulsar",
        "water_tank_with_tap",
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
                    "invoice",
                    "packet_list",
                    "license",
                ),
            },
        ),
        (
            _("Планшет Dell 7230"),
            {
                "fields": (
                    "pc_tablet_dell_7230",
                    "personalised_name_tag",
                    "ac_dc_power_adapter_dell",
                    "dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Ультразвуковая фазированная решетка PULSAR OEM 16/128"),
            {
                "fields": (
                    "ultrasonic_phased_array_pulsar",
                    "dcn",
                    "ab_back",
                    "gf_combo",
                    "ff_combo",
                    "ab_front",
                    "flange_50",
                    "manual_probs",
                    "has_dc_cable_battery",
                    "has_ethernet_cables",
                ),
            },
        ),
        (
            _("Дополнительное оборудование"),
            {
                "fields": (
                    "water_tank_with_tap",
                    "dc_battery_box",
                    "has_ac_dc_charger_adapter_battery",
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
            _("Сетевые настройки"),
            {
                "fields": (
                    "wifi_router_address",
                    "windows_password",
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


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    """Admin configuration for managing Licenses."""

    list_display = (
        "product",
        "license_short_key",
        "host_hwid",
        "device_hwid",
        "exp",
        "linked_equipment",
        "created_at",
    )
    list_filter = (
        "product",
        "exp",
        "created_at",
    )
    search_fields = (
        "license_key",
        "host_hwid",
        "device_hwid",
        "product",
        "company_name",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": (
                    "product",
                    "ver",
                    "company_name",
                    "exp",
                ),
            },
        ),
        (
            _("Аппаратные идентификаторы"),
            {
                "fields": (
                    "host_hwid",
                    "device_hwid",
                ),
            },
        ),
        (
            _("Функциональность"),
            {
                "fields": ("features",),
            },
        ),
        (
            _("Технические данные"),
            {
                "fields": (
                    "signature",
                    "license_key",
                ),
            },
        ),
        (
            _("Даты"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "license_key",
        "signature",
    )

    @admin.display(description=_("Ключ лицензии"))
    def license_short_key(self, obj: License) -> str:
        """Отображение короткой версии ключа лицензии."""
        if obj.license_key:
            key = obj.license_key
            if len(key) > 30:
                return f"{key[:20]}...{key[-10:]}"
            return key
        return "-"

    @admin.display(description=_("Привязанное оборудование"))
    def linked_equipment(self, obj: License) -> str:
        """Отображение привязанного оборудования."""
        if hasattr(obj, "kalmar32_license") and obj.kalmar32_license:
            return format_html(
                '<a href="/admin/core/kalmar32/{}/change/">Kalmar32: {}</a>',
                obj.kalmar32_license.id,
                obj.kalmar32_license.serial_number,
            )
        elif hasattr(obj, "phasar32_license") and obj.phasar32_license:
            return format_html(
                '<a href="/admin/core/phasar32/{}/change/">Phasar32: {}</a>',
                obj.phasar32_license.id,
                obj.phasar32_license.serial_number,
            )
        return "Не привязано"

    def has_add_permission(self, request):
        """Запрещаем добавление лицензий через админку (только через API)."""
        return False

    def has_change_permission(self, request, obj=None):
        """Разрешаем только просмотр, но не изменение."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление лицензий через админку."""
        return False


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for managing equipment reports."""

    list_display = (
        "report_date",
        "equipment_display",
        "number_to",
        "download_pdf",
        "download_json",
    )
    list_filter = (
        "report_date",
        "number_to",
    )
    search_fields = (
        "kalmar__serial_number",
        "kalmar__invoice",
        "phasar__serial_number",
        "phasar__invoice",
    )
    date_hierarchy = "report_date"
    ordering = ("-report_date",)

    fieldsets = (
        (
            _("Общие сведения"),
            {
                "fields": (
                    "kalmar",
                    "phasar",
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

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[Report]:
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("kalmar", "phasar")

    @admin.display(description=_("Оборудование"))
    def equipment_display(self, obj: Report) -> str:
        """Display equipment information."""
        if obj.kalmar:
            return f"Kalmar32: {obj.kalmar.serial_number}"
        if obj.phasar:
            return f"Phasar32: {obj.phasar.serial_number}"
        return "-"

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

    def formfield_for_foreignkey(
        self, db_field: Field, request: HttpRequest, **kwargs: object
    ) -> Field | None:
        """Limit choices for equipment fields to avoid conflicts."""
        if db_field.name == "kalmar":
            kwargs["queryset"] = Kalmar32.objects.all().order_by("serial_number")
        elif db_field.name == "phasar":
            kwargs["queryset"] = Phasar32.objects.all().order_by("serial_number")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
