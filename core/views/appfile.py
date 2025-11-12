"""API views for application file management.

This module provides file processing for Kalmar32 and Phasar32 application files.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Any, ClassVar

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class AppUploadPageView(View):
    """View for displaying the file upload page."""

    def get(self, request: HttpRequest) -> render:
        """Render upload page."""
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        return render(request, "app_upload.html", {"user": request.user})


class AuthCheckView(View):
    """Check if user is authenticated."""

    def get(self, request: HttpRequest) -> JsonResponse:
        """Check authentication status."""
        return JsonResponse(
            {
                "is_authenticated": request.user.is_authenticated,
                "is_staff": request.user.is_staff,
                "username": request.user.username
                if request.user.is_authenticated
                else None,
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class AppFileUploadView(View):
    """View for uploading application .exe files.

    Handles POST requests with file upload for Kalmar32/Phasar32 applications.
    Files are saved to media/apps/<type>/<yyyy_mm_dd>/<AppName>.exe
    """

    http_method_names: ClassVar[list[str]] = ["post"]
    ALLOWED_TYPES: ClassVar[tuple[str, ...]] = ("kalmar32", "phasar32")
    MAX_FILE_SIZE: ClassVar[int] = 500 * 1024 * 1024  # 500MB

    def post(self, request: HttpRequest) -> JsonResponse:
        """Upload application .exe file."""
        try:
            file_obj = self._get_uploaded_file(request)
            app_type = self._get_app_type(request)
            self._validate_file(file_obj, app_type)

            file_path = self._save_file(file_obj, app_type)
            return self._build_success_response(file_path, app_type)

        except ValidationError as e:
            return self._build_error_response(str(e), status=400)
        except Exception as e:
            logger.exception("App file upload failed")
            return self._build_error_response(str(e), status=500)

    def _get_uploaded_file(self, request: HttpRequest) -> object:
        """Extract uploaded file from request."""
        if not request.FILES:
            msg = "No file provided"
            raise ValidationError(msg)

        file_obj = request.FILES.get("file")
        if not file_obj:
            msg = "File field is required"
            raise ValidationError(msg)

        return file_obj

    def _get_app_type(self, request: HttpRequest) -> str:
        """Extract and validate application type."""
        app_type = request.POST.get("type", "").lower().strip()
        if not app_type:
            msg = "Type field is required"
            raise ValidationError(msg)

        if app_type not in self.ALLOWED_TYPES:
            msg = f"Type must be one of: {', '.join(self.ALLOWED_TYPES)}"
            raise ValidationError(msg)

        return app_type

    def _validate_file(self, file_obj: object, app_type: str) -> None:
        """Validate uploaded file."""
        if not file_obj.name.lower().endswith(".exe"):
            msg = "File must be a .exe file"
            raise ValidationError(msg)

        if file_obj.size > self.MAX_FILE_SIZE:
            msg = f"File size exceeds maximum of {self.MAX_FILE_SIZE} bytes"
            raise ValidationError(msg)

        # Validate file name based on type
        expected_name = "Kalmar.exe" if app_type == "kalmar32" else "Phasar.exe"
        if file_obj.name != expected_name:
            logger.warning(
                "File name %s doesn't match expected name %s for type %s",
                file_obj.name,
                expected_name,
                app_type,
            )

    def _save_file(self, file_obj: object, app_type: str) -> str:
        """Save file to media storage."""
        today = timezone.now().date()
        date_str = today.strftime("%Y_%m_%d")

        # Build file path: apps/<type>/<yyyy_mm_dd>/<AppName>.exe
        file_name = "Kalmar.exe" if app_type == "kalmar32" else "Phasar.exe"
        file_path = f"apps/{app_type}/{date_str}/{file_name}"

        # Ensure directory exists
        return default_storage.save(file_path, file_obj)

    def _build_success_response(self, file_path: str, app_type: str) -> JsonResponse:
        """Build success response."""
        response_data = {
            "status": "success",
            "message": "File uploaded successfully",
            "file_path": file_path,
            "app_type": app_type,
            "upload_date": timezone.now().date().isoformat(),
        }
        return JsonResponse(response_data, status=201)

    def _build_error_response(
        self, message: str, status: int = 400, detail: str = ""
    ) -> JsonResponse:
        """Build error response."""
        response_data = {
            "error": message,
            "status": "error",
            "detail": detail,
        }
        logger.error("App upload error: %s - %s", message, detail)
        return JsonResponse(response_data, status=status)


class AppFileDownloadView(View):
    """View for retrieving the latest application .exe file.

    Handles GET requests to download the most recent version of the application.
    """

    http_method_names: ClassVar[list[str]] = ["get"]
    ALLOWED_TYPES: ClassVar[tuple[str, ...]] = ("kalmar32", "phasar32")
    YEAR_LENGTH = 4
    MONTH_DAY_LENGTH = 2

    def get(self, request: HttpRequest, app_type: str) -> FileResponse | JsonResponse:  # noqa: ARG002
        """Get the latest application .exe file."""
        try:
            self._validate_app_type(app_type)
            file_info = self._find_latest_file(app_type)

            if not file_info:
                return self._build_error_response(
                    "No application file found", status=404
                )

            # Get the actual file path in the filesystem
            file_path = file_info["file_path"]

            if not default_storage.exists(file_path):
                return self._build_error_response("File not found", status=404)

            # Open the file and return it as a download response
            file = default_storage.open(file_path, "rb")
            file_name = Path(file_path).name

            response = FileResponse(
                file,
                as_attachment=True,
                filename=file_name,
                content_type="application/octet-stream",
            )

            # Add custom headers if needed
            response["Content-Disposition"] = f'attachment; filename="{file_name}"'

            return response  # noqa: TRY300

        except ValidationError as e:
            return self._build_error_response(str(e), status=400)
        except Exception as e:
            logger.exception("App file download failed")
            return self._build_error_response(str(e), status=500)

    def _validate_app_type(self, app_type: str) -> None:
        """Validate application type."""
        if app_type not in self.ALLOWED_TYPES:
            msg = f"Type must be one of: {', '.join(self.ALLOWED_TYPES)}"
            raise ValidationError(msg)

    def _find_latest_file(self, app_type: str) -> dict[str, Any] | None:
        """Find the most recent application file."""
        base_path = Path("apps") / app_type
        app_name = "Kalmar.exe" if app_type == "kalmar32" else "Phasar.exe"

        # Get all date directories
        date_dirs = []
        try:
            if default_storage.exists(str(base_path)):
                dirs, _ = default_storage.listdir(str(base_path))
                date_dirs = [d for d in dirs if self._is_valid_date_dir(d)]
        except (OSError, ValueError):
            logger.exception("Error listing directories")
            return None

        if not date_dirs:
            return None

        # Sort by date (newest first)
        date_dirs.sort(reverse=True)

        # Find the most recent file that exists
        for date_dir in date_dirs:
            file_path = base_path / date_dir / app_name
            if default_storage.exists(str(file_path)):
                return {
                    "file_path": str(file_path),
                    "file_url": self._get_file_url(str(file_path)),
                    "date": self._parse_date_from_dir(date_dir),
                    "app_type": app_type,
                    "file_name": app_name,
                }

        return None

    def _is_valid_date_dir(self, dir_name: str) -> bool:
        """Check if directory name is in valid date format (yyyy_mm_dd)."""
        try:
            year, month, day = dir_name.split("_")
            if (
                len(year) == self.YEAR_LENGTH
                and len(month) == self.MONTH_DAY_LENGTH
                and len(day) == self.MONTH_DAY_LENGTH
            ):
                date(int(year), int(month), int(day))
                return True
        except (ValueError, TypeError):
            pass
        return False

    def _parse_date_from_dir(self, dir_name: str) -> str:
        """Parse date from directory name."""
        try:
            year, month, day = dir_name.split("_")
        except (ValueError, TypeError):
            return dir_name
        else:
            return f"{year}-{month}-{day}"

    def _get_file_url(self, file_path: str) -> str:
        """Generate file URL for download."""
        # In production, this would be your CDN/media URL
        # For development, you might want to use Django's serve view
        return f"/media/{file_path}"

    def _build_success_response(self, file_info: dict[str, Any]) -> JsonResponse:
        """Build success response with file information."""
        response_data = {
            "status": "success",
            "file_url": file_info["file_url"],
            "file_path": file_info["file_path"],
            "app_type": file_info["app_type"],
            "file_name": file_info["file_name"],
            "date": file_info["date"],
            "download_url": file_info["file_url"],  # For backward compatibility
        }
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
        logger.error("App download error: %s - %s", message, detail)
        return JsonResponse(response_data, status=status)


@method_decorator(csrf_exempt, name="dispatch")
class AppFileListVersionsView(View):
    """View for listing all available versions of an application."""

    http_method_names: ClassVar[list[str]] = ["get"]
    ALLOWED_TYPES: ClassVar[tuple[str, ...]] = ("kalmar32", "phasar32")
    YEAR_LENGTH = 4
    MONTH_DAY_LENGTH = 2

    def get(self, request: HttpRequest, app_type: str) -> JsonResponse:  # noqa: ARG002
        """Get list of all available application versions."""
        try:
            self._validate_app_type(app_type)
            versions = self._find_all_versions(app_type)

            return JsonResponse(
                {
                    "status": "success",
                    "app_type": app_type,
                    "versions": versions,
                    "latest": versions[0] if versions else None,
                },
                status=200,
            )

        except ValidationError as e:
            return self._build_error_response(str(e), status=400)
        except Exception as e:
            logger.exception("App versions list failed")
            return self._build_error_response(str(e), status=500)

    def _validate_app_type(self, app_type: str) -> None:
        """Validate application type."""
        if app_type not in self.ALLOWED_TYPES:
            msg = f"Type must be one of: {', '.join(self.ALLOWED_TYPES)}"
            raise ValidationError(msg)

    def _find_all_versions(self, app_type: str) -> list[dict[str, Any]]:
        """Find all available versions of the application."""
        base_path = Path("apps") / app_type
        app_name = "Kalmar.exe" if app_type == "kalmar32" else "Phasar.exe"

        versions = []
        try:
            if default_storage.exists(str(base_path)):
                dirs, _ = default_storage.listdir(str(base_path))
                for dir_name in dirs:
                    if self._is_valid_date_dir(dir_name):
                        file_path = base_path / dir_name / app_name
                        if default_storage.exists(str(file_path)):
                            versions.append(
                                {
                                    "date": self._parse_date_from_dir(dir_name),
                                    "date_dir": dir_name,
                                    "file_path": str(file_path),
                                    "file_url": f"/media/{file_path}",
                                    "file_name": app_name,
                                }
                            )
        except (OSError, ValueError):
            logger.exception("Error listing versions")

        # Sort by date (newest first)
        versions.sort(key=lambda x: x["date_dir"], reverse=True)
        return versions

    def _is_valid_date_dir(self, dir_name: str) -> bool:
        """Check if directory name is in valid date format (yyyy_mm_dd)."""
        try:
            year, month, day = dir_name.split("_")
            if (
                len(year) == self.YEAR_LENGTH
                and len(month) == self.MONTH_DAY_LENGTH
                and len(day) == self.MONTH_DAY_LENGTH
            ):
                date(int(year), int(month), int(day))
                return True
        except (ValueError, TypeError):
            pass
        return False

    def _parse_date_from_dir(self, dir_name: str) -> str:
        """Parse date from directory name."""
        try:
            year, month, day = dir_name.split("_")
        except (ValueError, TypeError):
            return dir_name
        else:
            return f"{year}-{month}-{day}"

    def _build_error_response(
        self, message: str, status: int = 400, detail: str = ""
    ) -> JsonResponse:
        """Build error response."""
        response_data = {
            "error": message,
            "status": "error",
            "detail": detail,
        }
        return JsonResponse(response_data, status=status)
