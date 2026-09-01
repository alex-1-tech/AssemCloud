from django.utils.translation import gettext_lazy as _

KALMAR32_SCHEME_V1 = {
    "title": "Kalmar32 Specification Scheme v1",
    "model": "kalmar32",
    "version": 1,
    "sections": [
        {
            "key": "tablet_pc",
            "title": _("PC Tablet Components"),
            "fields": [
                {
                    "name": "pc_tablet_dell_7230",
                    "label": _("PC tablet Latitude Dell 7230"),
                    "cpp_name": "pcTabletDell7230",
                    "type": "string",
                },
                {
                    "name": "ac_dc_power_adapter_dell",
                    "label": _("AC/DC Power adapter for Dell 7230"),
                    "cpp_name": "acDcPowerAdapterDell",
                    "type": "string",
                },
                {
                    "name": "dc_charger_adapter_battery",
                    "label": _("DC Charger adapter for Dell 7230 from battery"),
                    "cpp_name": "dcChargerAdapterBattery",
                    "type": "string",
                },
            ],
        },
        {
            "key": "ultrasonic_hardware",
            "title": _("Ultrasonic Equipment"),
            "fields": [
                {
                    "name": "ultrasonic_phased_array_pulsar",
                    "label": _("Ultrasonic phased array PULSAR OEM 16/64 established"),
                    "cpp_name": "ultrasonicPhasedArrayPulsar",
                    "type": "string",
                },
                {
                    "name": "left_probs",
                    "label": _("Left probs PA2.25L16 1.1x10-17"),
                    "cpp_name": "leftProbs",
                    "type": "string",
                },
                {
                    "name": "right_probs",
                    "label": _("Right probs PA2.25L16 1.1x10-17"),
                    "cpp_name": "rightProbs",
                    "type": "string",
                },
                {
                    "name": "manual_probs",
                    "label": _("Manual probs PA2.25L16 0.9x10-17"),
                    "cpp_name": "manualProbs",
                    "type": "string",
                },
                {
                    "name": "straight_probs",
                    "label": _("Straight probs PA5.0L16 0.6x10-12"),
                    "cpp_name": "straightProbs",
                    "type": "string",
                },
            ],
        },
        {
            "key": "power_and_cables",
            "title": _("Power and Cables"),
            "fields": [
                {
                    "name": "dc_battery_box",
                    "label": _("DC Battery box established"),
                    "cpp_name": "dcBatteryBox",
                    "type": "string",
                },
                {
                    "name": "has_dc_cable_battery",
                    "label": _("DC Cable from Battery"),
                    "cpp_name": "hasDcCableBattery",
                    "type": "boolean",
                },
                {
                    "name": "has_ethernet_cables",
                    "label": _("Ethernet Cables"),
                    "cpp_name": "hasEthernetCables",
                    "type": "boolean",
                },
                {
                    "name": "has_ac_dc_charger_adapter_battery",
                    "label": _("AC/DC Charger adapter for battery"),
                    "cpp_name": "hasAcDcChargerAdapterBattery",
                    "type": "boolean",
                },
            ],
        },
        {
            "key": "calibration_and_tools",
            "title": _("Calibration and Tools"),
            "fields": [
                {
                    "name": "calibration_block_so_3r",
                    "label": _("Calibration bloc SO-3R"),
                    "cpp_name": "calibrationBlockSo3r",
                    "type": "string",
                },
                {
                    "name": "has_repair_tool_bag",
                    "label": _("Small repair tool with bag"),
                    "cpp_name": "hasRepairToolBag",
                    "type": "boolean",
                },
                {
                    "name": "has_installed_nameplate",
                    "label": _("Installed nameplate with serial number"),
                    "cpp_name": "hasInstalledNameplate",
                    "type": "boolean",
                },
            ],
        },
        {
            "key": "network_and_credentials",
            "title": _("Network and Security Settings"),
            "fields": [
                {
                    "name": "wifi_router_address",
                    "label": _("Wi-Fi router address"),
                    "cpp_name": "wifiRouterAddress",
                    "type": "string",
                },
                {
                    "name": "windows_password",
                    "label": _("Windows password"),
                    "cpp_name": "windowsPassword",
                    "type": "string",
                },
                {
                    "name": "license_password",
                    "label": _("License password"),
                    "cpp_name": "licensePassword",
                    "type": "string",
                },
            ],
        },
        {
            "key": "notes",
            "title": _("Additional Info"),
            "fields": [
                {
                    "name": "notes",
                    "label": _("Additional notes"),
                    "cpp_name": "notes",
                    "type": "text",
                },
            ],
        },
    ],
}