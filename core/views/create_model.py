"""API views for equipment management using unified Equipment model.

This module provides JSON API for creating/updating equipment records
using the generic Equipment, Model, and Scheme models.
"""
from __future__ import annotations

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

from core.models import Equipment, Model, Scheme

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class EquipmentCreateView(View):
    """View for creating/updating equipment records via JSON API using unified Equipment model.

    Expects JSON payload with at least 'serial_number' and 'equipment_type'.
    Optional fields: 'version', 'rail_type', 'invoice', 'packet_list', 'shipment_date'.
    All other fields are stored in 'other_data' JSONField.
    """

    http_method_names: ClassVar[list[str]] = ["post"]

    VALID_RAIL_TYPES = ("UIC60", "IRS52", "R65", "NONE")
    DEFAULT_VERSION = "Ver_1"
    DEFAULT_RAIL_TYPE = "NONE"

    def post(
        self,
        request: HttpRequest,
        model_name: str | None = None,
        *args: object,
        **kwargs: object,
    ) -> JsonResponse:
        """Create or update equipment record from JSON data."""
        try:
            data = self._extract_json(request)
        except ValidationError as e:
            return self._error_response(str(e), status=400)

            # Обязательные поля
            return self._error_response("Missing required field: serial_number", status=400)

        equipment_type = data.get("equipment_type")
        if not equipment_type:
            return self._error_response("Missing required field: equipment_type", status=400)

        # Проверка соответствия URL, если передан model_name
        if model_name and model_name != equipment_type:
            return self._error_response(
                f"URL model name '{model_name}' does not match equipment_type '{equipment_type}'",
                status=400,
            )

        version = data.get("version", self.DEFAULT_VERSION)
        rail_type = data.get("rail_type", self.DEFAULT_RAIL_TYPE).upper()
        if rail_type not in self.VALID_RAIL_TYPES:
            return self._error_response(f"Invalid rail_type: {rail_type}", status=400)

        try:
            model_obj, _ = Model.objects.get_or_create(
                name=equipment_type,
                version=version,
                type_rail=rail_type,
                defaults={"is_active": True},
            )
        except Exception as e:
            logger.exception("Failed to get_or_create Model")
            return self._error_response(f"Database error on Model: {e!s}", status=500)

        scheme_obj = Scheme.objects.filter(model_name=equipment_type, is_latest=True).first()
        if not scheme_obj:
            return self._error_response(
                f"No active Scheme found for model '{equipment_type}'. Please create a scheme first.",
                status=400,
            )

        serial_number = data.pop("serial_number")
        invoice = data.pop("invoice", "")
        packet_list = data.pop("packet_list", "")
        shipment_date = data.pop("shipment_date", None)

        other_data = data.copy()
        other_data.pop("equipment_type", None)
        other_data.pop("version", None)
        other_data.pop("rail_type", None)

        if shipment_date:
            if isinstance(shipment_date, str):
                try:
                    shipment_date = date.fromisoformat(shipment_date)
                except ValueError:
                    return self._error_response(
                        "Invalid shipment_date format, use YYYY-MM-DD",
                        status=400,
                    )
            elif not isinstance(shipment_date, date):
                return self._error_response(
                    "shipment_date must be a date or ISO string",
                    status=400,
                )

        try:
            with transaction.atomic():
                equipment, created = Equipment.objects.update_or_create(
                    serial_number=serial_number,
                    defaults={
                        "model": model_obj,
                        "scheme": scheme_obj,
                        "invoice": invoice,
                        "packet_list": packet_list,
                        "shipment_date": shipment_date,
                        "other_data": other_data,
                        # "license": license_obj,
                    },
                )
        except Exception as e:
            logger.exception("Failed to create/update Equipment")
            return self._error_response(f"Database error on Equipment: {e!s}", status=500)

        response_data = {
            "id": equipment.id,
            "serial_number": equipment.serial_number,
            "invoice": equipment.invoice,
            "packet_list": equipment.packet_list,
            "shipment_date": equipment.shipment_date.isoformat() if equipment.shipment_date else None,
            "license": equipment.license_id,
            "model": {
                "name": equipment.model.name,
                "version": equipment.model.version,
                "type_rail": equipment.model.type_rail,
            },
            "scheme": equipment.scheme_id,
            "status": "created" if created else "updated",
        }
        response_data.update(equipment.other_data)

        return JsonResponse(response_data, status=201 if created else 200)

    def _extract_json(self, request: HttpRequest) -> dict[str, Any]:
        """Extract and parse JSON data from request body."""
        try:
            return json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValidationError(f"Invalid JSON: {e!s}") from e

    def _error_response(self, message: str, status: int = 400, detail: str = "") -> JsonResponse:
        """Build standardized error response."""
        response_data = {"error": message, "status": "error"}
        if detail:
            response_data["detail"] = detail
        logger.error("EquipmentCreateView error: %s (detail: %s)", message, detail)
        return JsonResponse(response_data, status=status)
