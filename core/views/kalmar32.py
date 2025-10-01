"""API views for Kalmar32 equipment management.

This module provides direct JSON processing
for Kalmar32 model without using DRF serializers.
"""

import json
import logging
from datetime import date
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import Kalmar32

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class Kalmar32CreateView(View):
    """View for creating Kalmar32 equipment records via JSON API.

    Handles POST requests with JSON payload containing equipment data.
    Performs validation and creates new Kalmar32 instances.

    Attributes:
        http_method_names: List of allowed HTTP methods (POST only).

    """

    http_method_names: ClassVar[list[str]] = ["post"]

    REQUIRED_FIELDS: ClassVar[tuple[str]] = {"serial_number", "shipment_date"}
    DATE_FIELDS: ClassVar[tuple[str]] = {
        "shipment_date",
        "calibration_date",
    }
    BOOLEAN_FIELDS: ClassVar[tuple[str]] = {
        "has_tablet_screws",
        "has_ethernet_cable",
        "has_tool_kit",
    }
    FLOAT_FIELDS: ClassVar[tuple[str]] = {"weight"}

    def post(
        self,
        request: HttpRequest,
        *args: object,  #  # noqa: ARG002
    ) -> JsonResponse:
        """Create a new Kalmar32 equipment record from JSON data.

        Args:
            request: HTTP request object containing JSON payload.
            args: Additional positional arguments.

        Returns:
            JsonResponse: Response with created data or validation errors.

        Example:
            POST /api/kalmar32/
            {
                "serial_number": "KALMAR-123",
                "shipment_date": "2023-01-01",
                "weight": 12.5
            }

        """
        try:
            data = self._extract_request_data(request)
            self._validate_required_fields(data)
            processed_data = self._process_input_data(data)
            kalmar32 = self._create_kalmar32(processed_data)
            return self._build_success_response(kalmar32)
        except json.JSONDecodeError:
            return self._build_error_response("Invalid JSON", status=400)
        except ValidationError as e:
            return self._build_error_response(str(e), status=400)
        except ValueError as e:
            return self._build_error_response(
                "Invalid input", status=400, detail=str(e)
            )

    def _extract_request_data(self, request: HttpRequest) -> dict[str, Any]:
        """Extract and parse JSON data from request body."""
        try:
            return json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON format: {e}"
            raise ValidationError(msg) from e
        except UnicodeDecodeError as e:
            msg = f"Invalid encoding: {e}"
            raise ValidationError(msg) from e

    def _validate_required_fields(self, data: dict[str, Any]) -> None:
        """Validate presence of required fields.

        Args:
            data: Input data dictionary.

        Raises:
            ValidationError: If required fields are missing.

        """
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in data]
        if missing_fields:
            msg = f"Missing required fields: {', '.join(missing_fields)}"
            raise ValidationError(msg)

    def _process_input_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Convert and validate all field types."""
        processed = data.copy()
        processed = self._process_date_fields(processed)
        processed = self._process_boolean_fields(processed)
        return self._process_float_fields(processed)

    def _process_date_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        for field in self.DATE_FIELDS:
            if data.get(field):
                try:
                    data[field] = date.fromisoformat(data[field])
                except ValueError as e:
                    msg = f"Invalid date format for {field}: {e}"
                    raise ValidationError(msg) from e

        return data

    def _process_boolean_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        for field in self.BOOLEAN_FIELDS:
            if field in data:
                if isinstance(data[field], str):
                    data[field] = data[field].lower() in ("true", "1", "yes")
                elif not isinstance(data[field], bool):
                    data[field] = bool(data[field])
        return data

    def _process_float_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        for field in self.FLOAT_FIELDS:
            if field in data and data[field] is not None:
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError) as e:
                    msg = f"Invalid number for {field}: {e}"
                    raise ValidationError(msg) from e
        return data

    @transaction.atomic
    def _create_kalmar32(self, data: dict[str, Any]) -> Kalmar32:
        """Create Kalmar32 instance from validated data."""
        try:
            return Kalmar32.objects.update_or_create(
                serial_number=data["serial_number"], defaults=data
            )[0]
        except Exception as e:
            raise ValidationError(str(e)) from e

    def _build_success_response(self, kalmar32: Kalmar32) -> JsonResponse:
        """Build success response with created equipment data.

        Args:
            kalmar32: Created equipment instance.

        Returns:
            JsonResponse: JSON response with created data.

        """
        response_data = {
            "id": kalmar32.id,
            "serial_number": kalmar32.serial_number,
            "shipment_date": kalmar32.shipment_date.isoformat(),
            "status": "created",
        }
        return JsonResponse(response_data, status=201)

    def _build_success_response(self, kalmar32: Kalmar32) -> JsonResponse:
        """Build success response with all fields."""
        response_data = {
            "id": kalmar32.id,
            "serial_number": kalmar32.serial_number,
            "shipment_date": kalmar32.shipment_date.isoformat(),
            "case_number": kalmar32.case_number,
            "first_phased_array_converters": kalmar32.first_phased_array_converters,
            "second_phased_array_converters": kalmar32.second_phased_array_converters,
            "battery_case": kalmar32.battery_case,
            "aos_block": kalmar32.aos_block,
            "flash_drive": kalmar32.flash_drive,
            "co3r_measure": kalmar32.co3r_measure,
            "calibration_certificate": kalmar32.calibration_certificate,
            "calibration_date": kalmar32.calibration_date.isoformat()
            if kalmar32.calibration_date
            else None,
            "has_tablet_screws": kalmar32.has_tablet_screws,
            "has_ethernet_cable": kalmar32.has_ethernet_cable,
            "battery_charger": kalmar32.battery_charger,
            "tablet_charger": kalmar32.tablet_charger,
            "has_tool_kit": kalmar32.has_tool_kit,
            "software_check": kalmar32.software_check,
            "photo_video_url": kalmar32.photo_video_url,
            "weight": kalmar32.weight,
            "notes": kalmar32.notes,
            "manual_inclined": kalmar32.manual_inclined,
            "straight": kalmar32.straight,
            "photo_url": kalmar32.photo_url,
            "status": "created",
        }
        return JsonResponse(response_data, status=201)

    def _build_error_response(
        self, message: str, status: int = 400, detail: str = ""
    ) -> JsonResponse:
        """Build error response.

        Args:
            message: Primary error message.
            status: HTTP status code.
            detail: Additional error details.

        Returns:
            JsonResponse: Error response in JSON format.

        """
        response_data = {
            "error": message,
            "status": "error",
            "detail": detail,
        }
        msg = f"Validation error: {message!s}"
        logger.exception(msg)
        return JsonResponse(response_data, status=status)


@method_decorator(csrf_exempt, name="dispatch")
class Kalmar32GetReportsView(View):
    """View for retrieving Kalmar32 reports grouped by TO type.

    Returns JSON response with report dates grouped by TO type:
    {"TO-1": [date1, date2], "TO-2": [date3], "TO-3": []}
    """

    http_method_names: ClassVar[list[str]] = ["get"]

    def get(self, request: HttpRequest, pk: str) -> JsonResponse:  # noqa: ARG002
        """Get reports for specific Kalmar32 equipment grouped by TO type."""
        try:
            kalmar = Kalmar32.objects.get(serial_number=pk)
            reports = kalmar.reports.all()

            result = {"TO-1": [], "TO-2": [], "TO-3": []}

            for report in reports:
                to_type = report.number_to
                if to_type in result:
                    is_json = bool(report.json_report) and report.json_report.name != ""
                    is_pdf = bool(report.pdf_report) and report.pdf_report.name != ""
                    date = report.report_date.isoformat()
                    result[to_type].append(
                        {"date": date, "json": is_json, "pdf": is_pdf}
                    )

            return JsonResponse(result, status=200)

        except Kalmar32.DoesNotExist:
            return self._build_error_response("Kalmar32 not found", status=404)
        except (ValueError, AttributeError, TypeError) as e:
            return self._build_error_response(
                "Data processing error", status=500, detail=str(e)
            )

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
