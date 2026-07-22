"""Admin configuration for Kalmar32, Phasar01, Phasar02, Report, and License models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Kalmar32, License, Phasar01, Phasar02, Report

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
            _("Registration Data"),
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
            _("Dell 7230 Tablet"),
            {
                "fields": (
                    "pc_tablet_dell_7230",
                    "ac_dc_power_adapter_dell",
                    "dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Ultrasonic Phased Array PULSAR OEM 16/64"),
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
            _("Battery Pack"),
            {
                "fields": (
                    "dc_battery_box",
                    "has_ac_dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Calibration & Tools"),
            {
                "fields": (
                    "calibration_block_so_3r",
                    "has_repair_tool_bag",
                    "has_installed_nameplate",
                ),
            },
        ),
        (
            _("Network Settings"),
            {
                "fields": (
                    "wifi_router_address",
                    "windows_password",
                ),
            },
        ),
        (
            _("Additional Information"),
            {
                "fields": ("notes",),
            },
        ),
    )


@admin.register(Phasar01)
class Phasar01Admin(admin.ModelAdmin):
    """Admin configuration for managing Phasar01 equipment."""

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
            _("Registration Data"),
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
            _("Dell 7230 Tablet"),
            {
                "fields": (
                    "pc_tablet_dell_7230",
                    "ac_dc_power_adapter_dell",
                    "dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Ultrasonic Phased Array PULSAR OEM 16/128"),
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
            _("Additional Equipment"),
            {
                "fields": (
                    "water_tank_with_tap",
                    "dc_battery_box",
                    "has_ac_dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Calibration & Tools"),
            {
                "fields": (
                    "calibration_block_so_3r",
                    "has_repair_tool_bag",
                    "has_installed_nameplate",
                ),
            },
        ),
        (
            _("Network Settings"),
            {
                "fields": (
                    "wifi_router_address",
                    "windows_password",
                ),
            },
        ),
        (
            _("Additional Information"),
            {
                "fields": ("notes",),
            },
        ),
    )


@admin.register(Phasar02)
class Phasar02Admin(admin.ModelAdmin):
    """Admin configuration for managing Phasar02 equipment."""

    list_display = (
        "serial_number",
        "shipment_date",
        "invoice",
        "license",
    )
    list_filter = (
        "shipment_date",
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
            _("Registration Data"),
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
            _("Dell 7230 Tablet"),
            {
                "fields": (
                    "pc_tablet_dell_7230",
                    "ac_dc_power_adapter_dell",
                    "dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Ultrasonic Phased Array PULSAR OEM 16/128"),
            {
                "fields": (
                    "ultrasonic_phased_array_pulsar_left",
                    "ultrasonic_phased_array_pulsar_right",
                    "dcn_left",
                    "ab_back_left",
                    "gf_combo_left",
                    "ff_combo_left",
                    "ab_front_left",
                    "flange_50_left",
                    "manual_probs_left",
                    "has_dc_cable_battery_left",
                    "has_ethernet_cables_left",
                    "dcn_right",
                    "ab_back_right",
                    "gf_combo_right",
                    "ff_combo_right",
                    "ab_front_right",
                    "flange_50_right",
                    "manual_probs_right",
                    "has_dc_cable_battery_right",
                    "has_ethernet_cables_right",
                ),
            },
        ),
        (
            _("Additional Equipment"),
            {
                "fields": (
                    "water_tank_with_tap",
                    "dc_battery_box",
                    "has_ac_dc_charger_adapter_battery",
                ),
            },
        ),
        (
            _("Calibration & Tools"),
            {
                "fields": (
                    "calibration_block_so_3r",
                    "has_repair_tool_bag",
                    "has_installed_nameplate",
                ),
            },
        ),
        (
            _("Network Settings"),
            {
                "fields": (
                    "wifi_router_address",
                    "windows_password",
                ),
            },
        ),
        (
            _("Additional Information"),
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
            _("Main Information"),
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
            _("Hardware Identifiers"),
            {
                "fields": (
                    "host_hwid",
                    "device_hwid",
                ),
            },
        ),
        (
            _("Functionality"),
            {
                "fields": ("features",),
            },
        ),
        (
            _("Technical Data"),
            {
                "fields": (
                    "signature",
                    "license_key",
                ),
            },
        ),
        (
            _("Dates"),
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

    @admin.display(description=_("License Key"))
    def license_short_key(self, obj: License) -> str:
        """Display short version of license key."""
        if obj.license_key:
            key = obj.license_key
            if len(key) > 30:
                return f"{key[:20]}...{key[-10:]}"
            return key
        return "-"

    @admin.display(description=_("Linked Equipment"))
    def linked_equipment(self, obj: License) -> str:
        """Display linked equipment."""
        if hasattr(obj, "kalmar32_license") and obj.kalmar32_license:
            return format_html(
                '<a href="/admin/core/kalmar32/{}/change/">Kalmar32: {}</a>',
                obj.kalmar32_license.id,
                obj.kalmar32_license.serial_number,
            )
        if hasattr(obj, "phasar01_license") and obj.phasar01_license:
            return format_html(
                '<a href="/admin/core/phasar01/{}/change/">Phasar01: {}</a>',
                obj.phasar01_license.id,
                obj.phasar01_license.serial_number,
            )
        return "Not linked"


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
        "kalmar32_serial_number",
        "kalmar32__invoice",
        "phasar01__serial_number",
        "phasar01__invoice",
        "phasar02__serial_number",
        "phasar02__invoice",
    )
    date_hierarchy = "report_date"
    ordering = ("-report_date",)

    fieldsets = (
        (
            _("General Information"),
            {
                "fields": (
                    "kalmar32",
                    "phasar01",
                    "phasar02",
                    "report_date",
                    "number_to",
                ),
            },
        ),
        (
            _("Report Files"),
            {
                "fields": (
                    "json_report",
                    "pdf_report",
                ),
            },
        ),
        (
            _("Rail Records"),
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
        return super().get_queryset(request).select_related("kalmar32", "phasar01", "phasar02")

    @admin.display(description=_("Equipment"))
    def equipment_display(self, obj: Report) -> str:
        """Display equipment information."""
        if obj.kalmar32:
            return f"Kalmar32: {obj.kalmar32.serial_number}"
        if obj.phasar01:
            return f"Phasar01: {obj.phasar01.serial_number}"
        if obj.phasar02:
            return f"Phasar02: {obj.phasar02.serial_number}"
        return "-"

    @admin.display(description=_("Download PDF"))
    def download_pdf(self, obj: Report) -> str:
        """Provide a download link for the PDF report."""
        if obj.pdf_report:
            return format_html(
                '<a href="{}" target="_blank">📄 PDF</a>',
                obj.pdf_report.url,
            )
        return "-"

    @admin.display(description=_("Download JSON"))
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
        if db_field.name == "kalmar32":
            kwargs["queryset"] = Kalmar32.objects.all().order_by("serial_number")
        elif db_field.name == "phasar01":
            kwargs["queryset"] = Phasar01.objects.all().order_by("serial_number")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
