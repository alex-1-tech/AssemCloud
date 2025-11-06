"""API views for equipment report management.

This module provides direct file processing
for Report model without using DRF serializers.
Handles report creation (metadata) and file uploads in separate steps.
and uses equipment serial_number as an additional unique key when locating reports.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import TYPE_CHECKING, Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import Kalmar32, Phasar32, Report

if TYPE_CHECKING:
    from django.core.files.base import ContentFile
    from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class ReportCreateView(View):
    """View for creating equipment reports via API."""

    http_method_names: ClassVar[list[str]] = ["post"]
    REQUIRED_FIELDS: ClassVar[tuple[str, ...]] = (
        "serial_number",
        "upload_time",
        "number_to",
        "equipment_type",
    )

    def post(self, request: HttpRequest) -> JsonResponse:
        """Create a new report entry with metadata."""
        try:
            data = self._extract_request_data(request)
            metadata = self._parse_metadata(data)
            self._validate_metadata(metadata)

            equipment_type = metadata["equipment_type"]
            serial_number = metadata["serial_number"]
            equipment = self._get_equipment_device(equipment_type, serial_number)

            report_date = self._parse_report_date(metadata["upload_time"])
            number_to = metadata["number_to"]

            report = self._create_report(
                equipment=equipment,
                equipment_type=equipment_type,
                report_date=report_date,
                number_to=number_to,
            )

            return self._build_success_response(report)

        except json.JSONDecodeError:
            return self._build_error_response("Invalid JSON data", status=400)
        except ValidationError as e:
            return self._build_error_response(str(e), status=400)
        except (Kalmar32.DoesNotExist, Phasar32.DoesNotExist):
            return self._build_error_response("Equipment device not found", status=404)
        except Exception as e:
            logger.exception("Report creation failed")
            return self._build_error_response(str(e), status=500)

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

    def _raise_validation_error(self) -> None:
        msg = "Metadata is required"
        raise ValidationError(msg)

    def _parse_metadata(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract metadata from request data."""
        metadata = data.get("metadata", {})
        if not metadata:
            self._raise_validation_error()
        return metadata

    def _validate_metadata(self, metadata: dict[str, Any]) -> None:
        """Validate required metadata fields."""
        missing_fields = [
            field for field in self.REQUIRED_FIELDS if field not in metadata
        ]
        if missing_fields:
            msg = f"Missing required fields: {', '.join(missing_fields)}"
            raise ValidationError(msg)

        # Validate equipment_type
        equipment_type = metadata.get("equipment_type")
        if equipment_type not in ["kalmar32", "phasar32"]:
            msg = "Invalid equipment_type. Must be 'kalmar' or 'phasar'"
            raise ValidationError(msg)

    def _get_equipment_device(
        self, equipment_type: str, serial_number: str
    ) -> Kalmar32 | Phasar32:
        """Get equipment device by serial number."""
        if equipment_type == "kalmar32":
            return Kalmar32.objects.get(serial_number=serial_number)
        if equipment_type == "phasar32":
            return Phasar32.objects.get(serial_number=serial_number)
        msg = f"Unknown equipment type: {equipment_type}"
        raise ValidationError(msg)

    def _parse_report_date(self, date_str: str) -> date:
        """Parse and validate report date."""
        try:
            return date.fromisoformat(date_str)
        except ValueError as e:
            msg = f"Invalid date format: {e}"
            raise ValidationError(msg) from e

    @transaction.atomic
    def _create_report(
        self,
        equipment: Kalmar32 | Phasar32,
        equipment_type: str,
        report_date: date,
        number_to: str,
    ) -> Report:
        """Create Report instance from validated data."""
        try:
            if equipment_type == "kalmar32":
                return Report.objects.update_or_create(
                    kalmar=equipment, report_date=report_date, number_to=number_to
                )[0]
            return Report.objects.update_or_create(
                phasar=equipment, report_date=report_date, number_to=number_to
            )[0]
        except Exception as e:
            msg = f"Failed to create report: {e}"
            raise ValidationError(msg) from e

    def _build_success_response(self, report: Report) -> JsonResponse:
        """Build success response with created report data."""
        response_data = {
            "id": report.id,
            "report_date": report.report_date.isoformat(),
            "number_to": report.number_to,
            "status": "created",
        }

        # Add equipment-specific information
        if report.kalmar:
            response_data["equipment_type"] = "kalmar32"
            response_data["equipment_serial"] = report.kalmar.serial_number
        elif report.phasar:
            response_data["equipment_type"] = "phasar32"
            response_data["equipment_serial"] = report.phasar.serial_number

        return JsonResponse(response_data, status=201)

    def _build_error_response(
        self, message: str, status: int = 400, detail: str = ""
    ) -> JsonResponse:
        """Build error response."""
        logger.error("Report creation error: %s - %s", message, detail)
        return JsonResponse(
            {
                "error": message,
                "status": "error",
                "detail": detail,
            },
            status=status,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ReportFileUploadView(View):
    """View for uploading files to existing reports.

    Supports multipart POST and raw PUT.
    """

    http_method_names: ClassVar[list[str]] = ["put", "post"]
    MAX_FILE_SIZE: ClassVar[int] = 500 * 1024 * 1024  # 50MB
    FILE_TYPES: ClassVar[tuple[str, ...]] = ("pdf", "before", "after", "json")

    def post(
        self, request: HttpRequest, report_identifier: str, file_type: str
    ) -> JsonResponse:
        """Handle multipart/form-data POST uploads (recommended)."""
        return self._process_upload(request, report_identifier, file_type)

    def put(
        self, request: HttpRequest, report_identifier: str, file_type: str
    ) -> JsonResponse:
        """Handle PUT uploads (kept for compatibility)."""
        return self._process_upload(request, report_identifier, file_type)

    def _process_upload(
        self, request: HttpRequest, report_identifier: str, file_type: str
    ) -> JsonResponse:
        """Handle common upload operations for both POST and PUT requests."""
        try:
            self._validate_file_type(file_type)
            number_to = request.GET.get("number_to")
            report_date_str = request.GET.get("upload_time")
            equipment_type = request.GET.get("equipment_type")

            if not all([number_to, report_date_str, equipment_type]):
                msg = (
                    "For lookup by serial number, number_to, "
                    "upload_time and equipment_type are required"
                )
                raise ValidationError(msg)  # noqa: TRY301

            report_date = date.fromisoformat(report_date_str)
            report = self._get_report(
                report_identifier, number_to, report_date, equipment_type
            )
            file_obj = self._get_uploaded_file(request, file_type)
            self._validate_file_size(file_obj)

            self._save_file_to_report(report, file_type, file_obj)

            return self._build_success_response(report, file_type)

        except ValidationError as e:
            return self._build_error_response(str(e), status=400)
        except Report.DoesNotExist:
            return self._build_error_response("Report not found", status=404)
        except Exception as e:
            logger.exception("File upload failed")
            return self._build_error_response(str(e), status=500)

    def _validate_file_type(self, file_type: str) -> None:
        """Validate supported file types."""
        if file_type not in self.FILE_TYPES:
            msg = f"Invalid file type. Supported types: {', '.join(self.FILE_TYPES)}"
            raise ValidationError(msg)

    def _get_report(
        self,
        identifier: str,
        number_to: str | None = None,
        report_date: date | None = None,
        equipment_type: str | None = None,
    ) -> Report:
        """Get report by primary key or equipment serial_number."""
        try:
            return Report.objects.get(pk=identifier)
        except (ValueError, Report.DoesNotExist) as exc:
            if not all([number_to, report_date, equipment_type]):
                msg = (
                    "For lookup by serial number, number_to, report_date and "
                    "equipment_type are required"
                )
                raise ValidationError(msg) from exc

            if equipment_type == "kalmar32":
                return Report.objects.get(
                    kalmar__serial_number=identifier,
                    number_to=number_to,
                    report_date=report_date,
                )
            if equipment_type == "phasar32":
                return Report.objects.get(
                    phasar__serial_number=identifier,
                    number_to=number_to,
                    report_date=report_date,
                )
            msg = f"Unknown equipment type: {equipment_type}"
            raise ValidationError(msg) from exc

    def _get_uploaded_file(
        self,
        request: HttpRequest,
        file_type: str,  # noqa: ARG002
    ) -> UploadedFile | ContentFile:
        """Get uploaded file from request."""
        if request.FILES:
            if "file" in request.FILES:
                return request.FILES["file"]
            return next(iter(request.FILES.values()))
        return self._raise_no_file()

    def _validate_file_size(self, file_obj: UploadedFile | ContentFile) -> None:
        """Validate file size limit."""
        size = getattr(file_obj, "size", None)
        if size is None:
            try:
                file_obj.seek(0, 2)
                size = file_obj.tell()
                file_obj.seek(0)
            except AttributeError:
                size = 0
        if size > self.MAX_FILE_SIZE:
            msg = f"File exceeds maximum size of {self.MAX_FILE_SIZE} bytes"
            raise ValidationError(msg)

    def _save_file_to_report(
        self, report: Report, file_type: str, file_obj: UploadedFile | ContentFile
    ) -> None:
        """Save uploaded file to report instance."""
        field_map = {
            "pdf": "pdf_report",
            "before": "rail_record_before",
            "after": "rail_record_after",
            "json": "json_report",
        }
        field_name = field_map[file_type]
        getattr(report, field_name).save(file_obj.name, file_obj)
        report.save()

    def _build_success_response(self, report: Report, file_type: str) -> JsonResponse:
        """Build success response after file upload."""
        response_data = {
            "id": report.id,
            "report_date": report.report_date.isoformat(),
            "number_to": report.number_to,
            "file_type": file_type,
            "status": "file_uploaded",
        }

        # Add equipment-specific information
        if report.kalmar:
            response_data["equipment_type"] = "kalmar32"
            response_data["equipment_serial"] = report.kalmar.serial_number
        elif report.phasar:
            response_data["equipment_type"] = "phasar32"
            response_data["equipment_serial"] = report.phasar.serial_number

        return JsonResponse(response_data, status=200)

    def _build_error_response(
        self, message: str, status: int = 400, detail: str = ""
    ) -> JsonResponse:
        """Build error response."""
        logger.error("File upload error: %s - %s", message, detail)
        return JsonResponse(
            {
                "error": message,
                "status": "error",
                "detail": detail,
            },
            status=status,
        )
