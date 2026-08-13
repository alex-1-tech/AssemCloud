from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import Kalmar32, Phasar01, Phasar02


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