"""API views for Kalmar32 report management.

This module provides direct file processing for Report model without using DRF serializers.
Handles report creation (metadata) and file uploads in separate steps.
and uses kalmar.serial_number as an additional unique key when locating reports.
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

from core.models import Kalmar32, Report

if TYPE_CHECKING:
    from django.core.files.base import ContentFile
    from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class ReportCreateView(View):
    """View for creating Kalmar32 reports via API."""

    http_method_names: ClassVar[list[str]] = ["post"]
    REQUIRED_FIELDS: ClassVar[tuple[str, ...]] = (
        "serial_number",
        "upload_time",
        "number_to",
    )

    def post(self, request: HttpRequest) -> JsonResponse:
        """Create a new report entry with metadata."""
        try:
            data = self._extract_request_data(request)
            metadata = self._parse_metadata(data)
            self._validate_metadata(metadata)

            kalmar = self._get_kalmar_device(metadata["serial_number"])
            report_date = self._parse_report_date(metadata["upload_time"])
            number_to = metadata["number_to"]

            report = self._create_report(
                kalmar=kalmar, report_date=report_date, number_to=number_to
            )

            return self._build_success_response(report)

        except json.JSONDecodeError:
            return self._build_error_response("Invalid JSON data", status=400)
        except ValidationError as e:
            return self._build_error_response(str(e), status=400)
        except Kalmar32.DoesNotExist:
            return self._build_error_response("Kalmar device not found", status=404)
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

    def _parse_metadata(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract metadata from request data."""
        metadata = data.get("metadata", {})
        if not metadata:
            msg = "Metadata is required"
            raise ValidationError(msg)
        return metadata

    def _validate_metadata(self, metadata: dict[str, Any]) -> None:
        """Validate required metadata fields."""
        missing_fields = [
            field for field in self.REQUIRED_FIELDS if field not in metadata
        ]
        if missing_fields:
            msg = f"Missing required fields: {', '.join(missing_fields)}"
            raise ValidationError(msg)

    def _get_kalmar_device(self, serial_number: str) -> Kalmar32:
        """Get Kalmar32 device by serial number (unique key)."""
        return Kalmar32.objects.get(serial_number=serial_number)

    def _parse_report_date(self, date_str: str) -> date:
        """Parse and validate report date."""
        try:
            return date.fromisoformat(date_str)
        except ValueError as e:
            msg = f"Invalid date format: {e}"
            raise ValidationError(msg) from e

    @transaction.atomic
    def _create_report(
        self, kalmar: Kalmar32, report_date: date, number_to: str
    ) -> Report:
        """Create Report instance from validated data."""
        try:
            return Report.objects.update_or_create(
                kalmar=kalmar, report_date=report_date, number_to=number_to
            )[0]
        except Exception as e:
            msg = f"Failed to create report: {e}"
            raise ValidationError(msg) from e

    def _build_success_response(self, report: Report) -> JsonResponse:
        """Build success response with created report data."""
        return JsonResponse(
            {
                "id": report.id,
                "kalmar_serial": report.kalmar.serial_number,
                "report_date": report.report_date.isoformat(),
                "number_to": report.number_to,
                "status": "created",
            },
            status=201,
        )

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
    MAX_FILE_SIZE: ClassVar[int] = 50 * 1024 * 1024  # 50MB
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
            report_date = date.fromisoformat(report_date_str)
            report = self._get_report(report_identifier, number_to, report_date)
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
    ) -> Report:
        """Get report by primary key or kalmar serial_number."""
        try:
            return Report.objects.get(pk=identifier)
        except (ValueError, Report.DoesNotExist):
            if not all([number_to, report_date]):
                msg = "For lookup by serial number, \
                    both number_to and report_date are required"
                raise ValidationError(msg)
            return Report.objects.get(
                kalmar__serial_number=identifier,
                number_to=number_to,
                report_date=report_date,
            )

    def _get_uploaded_file(
        self,
        request: HttpRequest,
        file_type: str,  # noqa: ARG002
    ) -> UploadedFile | ContentFile:
        """Get uploaded file from request.

        Prefer 'file' field (common for QHttpMultiPart).
        Keep strict error if nothing found.
        """
        if request.FILES:
            if "file" in request.FILES:
                return request.FILES["file"]
            return next(iter(request.FILES.values()))

        msg = "No file uploaded"
        raise ValidationError(msg)

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
        return JsonResponse(
            {
                "id": report.id,
                "kalmar_serial": report.kalmar.serial_number,
                "report_date": report.report_date.isoformat(),
                "number_to": report.number_to,
                "file_type": file_type,
                "status": "file_uploaded",
            },
            status=200,
        )

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
