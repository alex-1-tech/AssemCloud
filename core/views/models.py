"""Unified API views for equipment management.

This module provides two view classes that handle all equipment models:
- EquipmentRetrieveView: for retrieving equipment data
- EquipmentReportsView: for retrieving equipment reports
"""

import logging
from datetime import date
from typing import Any, ClassVar

from django.db import models
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import Kalmar32, Phasar01, Phasar02, Report

logger = logging.getLogger(__name__)


# Registry of available equipment models
EQUIPMENT_MODELS: dict[str, type[models.Model]] = {
    "phasar01": Phasar01,
    "phasar02": Phasar02,
    "kalmar32": Kalmar32,
}


def convert_phasar01(equipment: Phasar01) -> dict[str, Any]:
    """Convert Phasar01 to dictionary with specific field names."""
    return {
        "id": equipment.id,
        "serial_number": equipment.serial_number,
        "shipment_date": equipment.shipment_date.isoformat(),
        "invoice": equipment.invoice,
        "packet_list": equipment.packet_list,
        # PC tablet Latitude Dell 7230
        "pc_tablet_dell_7230": equipment.pc_tablet_dell_7230,
        "ac_dc_power_adapter_dell": equipment.ac_dc_power_adapter_dell,
        "dc_charger_adapter_battery": equipment.dc_charger_adapter_battery,
        # Ultrasonic phased array PULSAR OEM 16/128
        "ultrasonic_phased_array_pulsar": equipment.ultrasonic_phased_array_pulsar,
        "dcn": equipment.dcn,
        "ab_back": equipment.ab_back,
        "gf_combo": equipment.gf_combo,
        "ff_combo": equipment.ff_combo,
        "ab_front": equipment.ab_front,
        "flange_50": equipment.flange_50,
        "manual_probs": equipment.manual_probs,
        "has_dc_cable_battery": equipment.has_dc_cable_battery,
        "has_ethernet_cables": equipment.has_ethernet_cables,
        "water_tank_with_tap": equipment.water_tank_with_tap,
        # DC Battery box
        "dc_battery_box": equipment.dc_battery_box,
        "has_ac_dc_charger_adapter_battery": equipment.has_ac_dc_charger_adapter_battery,
        # Calibration and tools
        "calibration_block_so_3r": equipment.calibration_block_so_3r,
        "has_repair_tool_bag": equipment.has_repair_tool_bag,
        "has_installed_nameplate": equipment.has_installed_nameplate,
        # network settings
        "wifi_router_address": equipment.wifi_router_address,
        "windows_password": equipment.windows_password,
        # Additional fields
        "notes": equipment.notes,
    }


def convert_phasar02(equipment: Phasar02) -> dict[str, Any]:
    """Convert Phasar02 to dictionary with specific field names."""
    return {
        "id": equipment.id,
        "serial_number": equipment.serial_number,
        "license": equipment.license.id if equipment.license else None,
        "license_password": equipment.license_password,
        "shipment_date": equipment.shipment_date.isoformat(),
        "invoice": equipment.invoice,
        "packet_list": equipment.packet_list,
        # PC tablet Latitude Dell 7230
        "pc_tablet_dell_7230": equipment.pc_tablet_dell_7230,
        "ac_dc_power_adapter_dell": equipment.ac_dc_power_adapter_dell,
        "dc_charger_adapter_battery": equipment.dc_charger_adapter_battery,
        # Ultrasonic phased array PULSAR OEM 16/128 (LEFT)
        "ultrasonic_phased_array_pulsar_left": equipment.ultrasonic_phased_array_pulsar_left,
        "dcn_left": equipment.dcn_left,
        "ab_back_left": equipment.ab_back_left,
        "gf_combo_left": equipment.gf_combo_left,
        "ff_combo_left": equipment.ff_combo_left,
        "ab_front_left": equipment.ab_front_left,
        "flange_50_left": equipment.flange_50_left,
        "manual_probs_left": equipment.manual_probs_left,
        "has_dc_cable_battery_left": equipment.has_dc_cable_battery_left,
        "has_ethernet_cables_left": equipment.has_ethernet_cables_left,
        # Ultrasonic phased array PULSAR OEM 16/128 (RIGHT)
        "ultrasonic_phased_array_pulsar_right": equipment.ultrasonic_phased_array_pulsar_right,
        "dcn_right": equipment.dcn_right,
        "ab_back_right": equipment.ab_back_right,
        "gf_combo_right": equipment.gf_combo_right,
        "ff_combo_right": equipment.ff_combo_right,
        "ab_front_right": equipment.ab_front_right,
        "flange_50_right": equipment.flange_50_right,
        "manual_probs_right": equipment.manual_probs_right,
        "has_dc_cable_battery_right": equipment.has_dc_cable_battery_right,
        "has_ethernet_cables_right": equipment.has_ethernet_cables_right,
        # Water tanks
        "water_tank_with_tap": equipment.water_tank_with_tap,
        # DC Battery boxes
        "dc_battery_box": equipment.dc_battery_box,
        "has_ac_dc_charger_adapter_battery": equipment.has_ac_dc_charger_adapter_battery,
        # Calibration blocks
        "calibration_block_so_3r": equipment.calibration_block_so_3r,
        # Repair tools
        "has_repair_tool_bag": equipment.has_repair_tool_bag,
        # Nameplates
        "has_installed_nameplate": equipment.has_installed_nameplate,
        # network settings
        "wifi_router_address": equipment.wifi_router_address,
        "windows_password": equipment.windows_password,
        # Additional fields
        "notes": equipment.notes,
    }


def convert_kalmar32(equipment: Kalmar32) -> dict[str, Any]:
    """Convert Kalmar32 to dictionary with specific field names."""
    return {
        "id": equipment.id,
        "serial_number": equipment.serial_number,
        "shipment_date": equipment.shipment_date.isoformat(),
        "invoice": equipment.invoice,
        "packet_list": equipment.packet_list,
        # PC tablet Latitude Dell 7230
        "pc_tablet_dell_7230": equipment.pc_tablet_dell_7230,
        "ac_dc_power_adapter_dell": equipment.ac_dc_power_adapter_dell,
        "dc_charger_adapter_battery": equipment.dc_charger_adapter_battery,
        # Ultrasonic phased array PULSAR OEM 16/64
        "ultrasonic_phased_array_pulsar": equipment.ultrasonic_phased_array_pulsar,
        "left_probs": equipment.left_probs,
        "right_probs": equipment.right_probs,
        "manual_probs": equipment.manual_probs,
        "straight_probs": equipment.straight_probs,
        "has_dc_cable_battery": equipment.has_dc_cable_battery,
        "has_ethernet_cables": equipment.has_ethernet_cables,
        # DC Battery box
        "dc_battery_box": equipment.dc_battery_box,
        "has_ac_dc_charger_adapter_battery": equipment.has_ac_dc_charger_adapter_battery,
        # Calibration and tools
        "calibration_block_so_3r": equipment.calibration_block_so_3r,
        "has_repair_tool_bag": equipment.has_repair_tool_bag,
        "has_installed_nameplate": equipment.has_installed_nameplate,
        # network settings
        "wifi_router_address": equipment.wifi_router_address,
        "windows_password": equipment.windows_password,
        # Additional fields
        "notes": equipment.notes,
    }


class BaseEquipmentView(View):
    """Base class with common functionality for equipment views."""

    def _get_model_class(self, model_name: str) -> type[models.Model]:
        """Get model class by name."""
        model_name = model_name.lower()
        if model_name not in EQUIPMENT_MODELS:
            available = ", ".join(EQUIPMENT_MODELS.keys())
            msg = f"Unknown model: {model_name}. Available models: {available}"
            raise ValueError(msg)
        return EQUIPMENT_MODELS[model_name]

    def _get_equipment(self, model_class: type[models.Model], serial_number: str) -> models.Model:
        """Retrieve equipment instance by serial number."""
        try:
            return model_class.objects.get(serial_number=serial_number)
        except model_class.DoesNotExist:
            msg = f"Equipment with serial number {serial_number} not found"
            logger.warning(msg)
            raise
        except Exception as e:
            msg = f"Database error: {e}"
            logger.exception(msg)
            raise

    def _build_error_response(self, message: str, status: int = 400, detail: str = "") -> JsonResponse:
        """Build error response."""
        response_data = {
            "error": message,
            "status": "error",
            "detail": detail,
        }
        logger.error("Error: %s, Detail: %s", message, detail)
        return JsonResponse(response_data, status=status)


@method_decorator(csrf_exempt, name="dispatch")
class EquipmentRetrieveView(BaseEquipmentView):
    """Unified view for retrieving equipment data.

    Handles GET requests to retrieve equipment data by serial number.
    URL pattern: /api/equipment/<model_name>/<serial_number>/
    """

    http_method_names: ClassVar[list[str]] = ["get"]

    def get(self, request: HttpRequest, model_name: str, serial_number: str) -> JsonResponse:  # noqa: ARG002
        """Retrieve equipment data by serial number."""
        try:
            # Validate and get model class
            model_class = self._get_model_class(model_name)

            # Get equipment instance
            equipment = self._get_equipment(model_class, serial_number)

            # Convert to dict based on model type
            response_data = self._convert_to_dict(equipment, model_name)
            response_data["status"] = "retrieved"
            response_data["model_type"] = model_name

            return JsonResponse(response_data, status=200)

        except ValueError as e:
            return self._build_error_response(str(e), status=400)
        except models.ObjectDoesNotExist:
            return self._build_error_response("Equipment not found", status=404)
        except Exception as e:
            logger.exception("Unexpected error")
            return self._build_error_response("Internal server error", status=500, detail=str(e))

    def _convert_to_dict(self, equipment: models.Model, model_name: str) -> dict[str, Any]:
        """Convert equipment model instance to dictionary based on model type."""
        converters = {
            "phasar01": convert_phasar01,
            "phasar02": convert_phasar02,
            "kalmar32": convert_kalmar32,
        }

        converter = converters.get(model_name)
        if converter:
            return converter(equipment)

        # Fallback to generic conversion for unknown models
        error_msg = f"No specific converter for {model_name}, using generic conversion"
        logger.warning(error_msg)
        return self._generic_convert(equipment)

    def _generic_convert(self, equipment: models.Model) -> dict[str, Any]:
        """Generate conversion for any model."""
        data = {}
        for field in equipment._meta.fields:  # noqa: SLF001
            value = getattr(equipment, field.name)
            if isinstance(value, date):
                value = value.isoformat()
            elif isinstance(value, models.Model):
                value = value.id if value else None
            data[field.name] = value
        return data


@method_decorator(csrf_exempt, name="dispatch")
class EquipmentReportsView(BaseEquipmentView):
    """Unified view for retrieving equipment reports.

    Handles GET requests to retrieve equipment reports by serial number.
    URL pattern: /api/equipment/<model_name>/<serial_number>/reports/

    Returns JSON response with report dates grouped by TO type:
    {"TO-1": ["2025-10-31", "2025-10-30"], "TO-2": ["2025-10-29"], "TO-3": []}
    """

    http_method_names: ClassVar[list[str]] = ["get"]

    def get(self, request: HttpRequest, model_name: str, serial_number: str) -> JsonResponse:  # noqa: ARG002
        """Get reports for specific equipment grouped by TO type."""
        try:
            # Validate and get model class
            model_class = self._get_model_class(model_name)

            # Get equipment instance (just to verify it exists)
            equipment = self._get_equipment(model_class, serial_number)

            # Get reports for this equipment
            reports = self._get_reports_for_equipment(model_name, equipment)

            # Group by TO type and format dates
            result = self._group_reports_with_status(reports)

            # Add metadata
            result["model_type"] = model_name
            result["serial_number"] = serial_number

            return JsonResponse(result, status=200)

        except ValueError as e:
            return self._build_error_response(str(e), status=400)
        except models.ObjectDoesNotExist:
            return self._build_error_response("Equipment not found", status=404)
        except (AttributeError, TypeError) as e:
            return self._build_error_response("Data processing error", status=500, detail=str(e))

    def _get_reports_for_equipment(self, model_name: str, equipment: models.Model) -> list[dict]:
        """Retrieve reports for specific equipment."""
        try:
            filter_kwargs = {model_name: equipment}
            reports = (
                Report.objects.filter(**filter_kwargs)
                .values("number_to", "report_date", "json_report", "pdf_report")
                .order_by("-report_date")
            )
            return list(reports)
        except Exception as e:
            msg = f"Error fetching reports: {e}"
            logger.exception(msg)
            return []

    def _group_reports_with_status(self, reports: list[dict]) -> dict[str, list[dict]]:
        """Group reports by TO type with file existence status."""
        result = {"TO-1": [], "TO-2": [], "TO-3": []}

        for report in reports:
            to_type = report.get("number_to")
            report_date = report.get("report_date")

            if to_type not in result:
                continue

            if isinstance(report_date, date):
                date_str = report_date.isoformat()
                json_exists = bool(report.get("json_report"))
                pdf_exists = bool(report.get("pdf_report"))

                report_data = {"date": date_str, "json": json_exists, "pdf": pdf_exists}

                if not any(item["date"] == date_str for item in result[to_type]):
                    result[to_type].append(report_data)

        # Sort each TO type list by date
        for entries in result.values():
            entries.sort(key=lambda x: x["date"], reverse=True)

        return result
