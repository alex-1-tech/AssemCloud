"""API views for equipment management with dynamic model selection.

This module provides unified JSON processing for both Kalmar32 and Phasar32 models
with automatic model selection based on equipment_type field.
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

from core.models import Kalmar32, Phasar32
from core.views.kalmar32 import build_kalmar32_response_data
from core.views.phasar32 import build_phasar32_response_data

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class EquipmentCreateView(View):
    """View for creating equipment records via JSON API with dynamic model selection.

    Handles POST requests with JSON payload containing equipment data.
    Automatically selects Kalmar32 or Phasar32 based on equipment_type field.
    """

    http_method_names: ClassVar[list[str]] = ["post"]

    REQUIRED_FIELDS: ClassVar[tuple[str]] = {
        "serial_number",
        "shipment_date",
        "equipment_type",
    }
    VALID_EQUIPMENT_TYPES: ClassVar[tuple[str]] = ("kalmar32", "phasar32")

    DATE_FIELDS: ClassVar[tuple[str]] = {
        "shipment_date",
    }

    BOOLEAN_FIELDS: ClassVar[tuple[str]] = {
        "has_dc_cable_battery",
        "has_ethernet_cables",
        "has_repair_tool_bag",
        "has_installed_nameplate",
    }

    MODEL_CONFIGS: ClassVar[dict] = {
        "kalmar32": {
            "model": Kalmar32,
            "response_builder": build_kalmar32_response_data,
        },
        "phasar32": {
            "model": Phasar32,
            "response_builder": build_phasar32_response_data,
        },
    }

    def post(
        self,
        request: HttpRequest,
        *args: object,  # noqa: ARG002
    ) -> JsonResponse:
        """Create a new equipment record from JSON data with dynamic model selection."""
        try:
            data = self._extract_request_data(request)
            self._validate_required_fields(data)

            equipment_type = data.pop("equipment_type")
            model_config = self.MODEL_CONFIGS[equipment_type]

            processed_data = self._process_input_data(data, model_config)
            equipment = self._create_equipment(
                equipment_type, model_config, processed_data
            )

            return self._build_success_response(
                equipment, model_config["response_builder"]
            )

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

    def _process_input_data(
        self, data: dict[str, Any], model_config: dict
    ) -> dict[str, Any]:
        """Convert and validate all field types for specific model."""
        processed = data.copy()
        return self._process_boolean_fields(processed)

    def _process_boolean_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process boolean fields."""
        for field in self.BOOLEAN_FIELDS:
            if field in data:
                if isinstance(data[field], str):
                    data[field] = data[field].lower() in ("true", "1", "yes")
                elif not isinstance(data[field], bool):
                    data[field] = bool(data[field])
        return data

    @transaction.atomic
    def _create_equipment(
        self, equipment_type: str, model_config: dict, data: dict[str, Any]
    ):
        """Create equipment instance from validated data."""
        try:
            model_class = model_config["model"]
            return model_class.objects.update_or_create(
                serial_number=data["serial_number"], defaults=data
            )[0]
        except Exception as e:
            msg = f"Error creating {equipment_type}: {e!s}"
            raise ValidationError(msg) from e

    def _build_success_response(self, equipment, response_builder) -> JsonResponse:
        """Build success response with created equipment data."""
        response_data = response_builder(equipment, "created")
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
