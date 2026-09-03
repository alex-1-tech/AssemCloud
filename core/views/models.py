"""Unified API views for equipment management.

This module provides view classes for retrieving equipment data
using the new unified Equipment model with dynamic schemes.
"""

import logging

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import Equipment

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class EquipmentRetrieveView(View):
    """Unified view for retrieving equipment data by serial number.

    Works with the new Equipment model and returns all fields,
    including dynamic data from other_data JSONField.
    URL pattern: /api/<model_name>/<serial_number>/get_settings
    """

    http_method_names = ["get"]

    def get(self, request: HttpRequest, model_name: str, serial_number: str) -> JsonResponse:
        """Retrieve equipment data by serial number using unified Equipment model."""
        try:
            equipment = Equipment.objects.select_related("model", "scheme", "license").get(
                serial_number=serial_number
            )
        except Equipment.DoesNotExist:
            return self._error_response("Equipment not found", status=404)

        if equipment.model.equipment_type.name != model_name:
            return self._error_response(
                f"Model name mismatch: expected '{model_name}', got '{equipment.model.equipment_type.name}'",
                status=400,
            )

        response_data = {
            "id": equipment.id,
            "serial_number": equipment.serial_number,
            "invoice": equipment.invoice,
            "packet_list": equipment.packet_list,
            "shipment_date": (equipment.shipment_date.isoformat() if equipment.shipment_date else None),
            "license": equipment.license_id,
            "model": {
                "name": equipment.model.equipment_type.name,
                "version": equipment.model.version,
                "type_rail": equipment.model.type_rail,
            },
            "scheme": {
                "id": equipment.scheme.id if equipment.scheme else None,
                "version": equipment.scheme.version if equipment.scheme else None,
            },
            "other_data": equipment.other_data,
            "status": "retrieved",
            "model_type": model_name,
        }

        return JsonResponse(response_data, status=200)

    def _error_response(self, message: str, status: int = 400) -> JsonResponse:
        """Build standardized error response."""
        logger.error("EquipmentRetrieveView error: %s", message)
        return JsonResponse({"error": message, "status": "error"}, status=status)
