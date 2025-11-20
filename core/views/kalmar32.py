"""API views for Kalmar32 equipment management.

This module provides direct JSON processing
for Kalmar32 model without using DRF serializers.
"""

import logging
from datetime import date
from typing import Any, ClassVar

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import Kalmar32, Report

logger = logging.getLogger(__name__)


def build_kalmar32_response_data(
    kalmar32: Kalmar32, status_message: str
) -> dict[str, Any]:
    """Build standardized response data for Kalmar32 objects."""
    return {
        "id": kalmar32.id,
        "serial_number": kalmar32.serial_number,
        "shipment_date": kalmar32.shipment_date.isoformat(),
        "case_number": kalmar32.case_number,
        # PC tablet Latitude Dell 7230
        "pc_tablet_dell_7230": kalmar32.pc_tablet_dell_7230,
        "ac_dc_power_adapter_dell": kalmar32.ac_dc_power_adapter_dell,
        "dc_charger_adapter_battery": kalmar32.dc_charger_adapter_battery,
        # Ultrasonic phased array PULSAR OEM 16/64
        "ultrasonic_phased_array_pulsar": kalmar32.ultrasonic_phased_array_pulsar,
        "left_probs": kalmar32.left_probs,
        "left_probs_date": kalmar32.left_probs_date,
        "right_probs": kalmar32.right_probs,
        "right_probs_date": kalmar32.right_probs_date,
        "manual_probs": kalmar32.manual_probs,
        "manual_probs_date": kalmar32.manual_probs_date,
        "straight_probs": kalmar32.straight_probs,
        "straight_probs_date": kalmar32.straight_probs_date,
        "has_dc_cable_battery": kalmar32.has_dc_cable_battery,
        "has_ethernet_cables": kalmar32.has_ethernet_cables,
        # DC Battery box
        "dc_battery_box": kalmar32.dc_battery_box,
        "ac_dc_charger_adapter_battery": kalmar32.ac_dc_charger_adapter_battery,
        # Calibration and tools
        "calibration_block_so_3r": kalmar32.calibration_block_so_3r,
        "has_repair_tool_bag": kalmar32.has_repair_tool_bag,
        "has_installed_nameplate": kalmar32.has_installed_nameplate,
        # network settings
        "wifi_router_address": kalmar32.wifi_router_address,
        "windows_password": kalmar32.windows_password,
        # Additional fields
        "notes": kalmar32.notes,
        "status": status_message,
    }


@method_decorator(csrf_exempt, name="dispatch")
class Kalmar32GetReportsView(View):
    """View for retrieving Kalmar32 reports grouped by TO type.

    Returns JSON response with report dates grouped by TO type:
    {"TO-1": ["2025-10-31", "2025-10-30"], "TO-2": ["2025-10-29"], "TO-3": []}
    """

    http_method_names: ClassVar[list[str]] = ["get"]

    def get(self, request: HttpRequest, pk: str) -> JsonResponse:  # noqa: ARG002
        """Get reports for specific Kalmar32 equipment grouped by TO type."""
        try:
            # Verify Kalmar32 exists
            kalmar32 = Kalmar32.objects.get(serial_number=pk)

            # Get reports for this equipment
            reports = self._get_reports_for_equipment(kalmar32)

            # Group by TO type and format dates
            result = self._group_reports_with_status(reports)

            return JsonResponse(result, status=200)

        except Kalmar32.DoesNotExist:
            return self._build_error_response("Kalmar32 not found", status=404)
        except (ValueError, AttributeError, TypeError) as e:
            return self._build_error_response(
                "Data processing error", status=500, detail=str(e)
            )

    def _get_reports_for_equipment(self, kalmar32: Kalmar32) -> list[dict]:
        """Retrieve reports for specific Kalmar32 equipment."""
        try:
            reports = (
                Report.objects.filter(kalmar=kalmar32)
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

                # Check if files exist
                json_exists = bool(report.get("json_report"))
                pdf_exists = bool(report.get("pdf_report"))

                report_data = {"date": date_str, "json": json_exists, "pdf": pdf_exists}

                if not any(item["date"] == date_str for item in result[to_type]):
                    result[to_type].append(report_data)

        for entries in result.values():
            entries.sort(key=lambda x: x["date"], reverse=True)

        return result

    def _build_error_response(
        self, message: str, status: int = 400, detail: str = ""
    ) -> JsonResponse:
        """Build error response."""
        response_data = {
            "error": message,
            "status": "error",
            "detail": detail,
        }
        logger.error("Error: %s, Detail: %s", message, detail)
        return JsonResponse(response_data, status=status)


class Kalmar32RetrieveView(View):
    """View for retrieving Kalmar32 equipment records via JSON API.

    Handles GET requests to retrieve equipment data by serial number.
    Returns complete equipment data in JSON format.
    """

    http_method_names: ClassVar[list[str]] = ["get"]

    def get(
        self,
        request: HttpRequest,  # noqa: ARG002
        pk: str,
    ) -> JsonResponse:
        """Retrieve a Kalmar32 equipment record by serial number."""
        try:
            kalmar32 = self._get_kalmar32(pk)
            return self._build_success_response(kalmar32)
        except Kalmar32.DoesNotExist:
            return self._build_error_response("Equipment not found", status=404)
        except Exception as e:  # noqa: BLE001
            return self._build_error_response(
                "Internal server error", status=500, detail=str(e)
            )

    def _get_kalmar32(self, serial_number: str) -> Kalmar32:
        """Retrieve Kalmar32 instance by serial number."""
        try:
            return Kalmar32.objects.get(serial_number=serial_number)
        except Kalmar32.DoesNotExist:
            msg = f"Equipment with serial number {serial_number} not found"
            logger.exception(msg)
            raise
        except Exception as e:
            msg = f"Database error: {e}"
            logger.exception(msg)
            raise

    def _build_success_response(self, kalmar32: Kalmar32) -> JsonResponse:
        """Build success response with equipment data."""
        response_data = build_kalmar32_response_data(kalmar32, "retrieved")
        return JsonResponse(response_data, status=200)

    def _build_error_response(
        self, message: str, status: int = 400, detail: str = ""
    ) -> JsonResponse:
        """Build error response."""
        response_data = {
            "error": message,
            "status": "error",
            "detail": detail,
        }
        logger.error("Error: %s, Detail: %s", message, detail)
        return JsonResponse(response_data, status=status)
