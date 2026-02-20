"""API views for application file management.

This module provides file processing for Kalmar32, Phasar32, and ManualApp application files.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
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
import contextlib

logger = logging.getLogger(__name__)


class BaseAppVersionView(View, ABC):
    """Base class for application version management views.

    Provides common functionality for handling application files and versions.
    """

    ALLOWED_TYPES: ClassVar[tuple[str, ...]] = ("kalmar32", "phasar32", "manual_app")
    ALLOWED_RAIL_TYPES: ClassVar[tuple[str, ...]] = ("P65", "IRS52", "UIC60")
    YEAR_LENGTH: ClassVar[int] = 4
    MONTH_DAY_LENGTH: ClassVar[int] = 2

    @property
    @abstractmethod
    def app_name_map(self) -> dict[str, str]:
        """Map application types to their executable names."""
        return {
            "kalmar32": "Kalmar.exe",
            "phasar32": "Phasar.exe",
            "manual_app": "ManualApp.exe",
        }

    def get_app_name(self, app_type: str) -> str:
        """Get executable name for application type."""
        return self.app_name_map.get(app_type, "")

    def validate_app_type(self, app_type: str) -> str | None:
        """Validate application type and return error response if invalid."""
        if app_type not in self.ALLOWED_TYPES:
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Invalid application type: '{app_type}'",
                    "detail": f"Application type must be one of: {', '.join(self.ALLOWED_TYPES)}",
                    "provided_type": app_type,
                    "allowed_types": list(self.ALLOWED_TYPES),
                },
                status=400,
            )
        return None

    def validate_rail_type(self, rail_type: str | None) -> str | None:
        """Validate rail type and return error response if invalid."""
        if rail_type and rail_type not in self.ALLOWED_RAIL_TYPES:
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Invalid rail type: '{rail_type}'",
                    "detail": f"Rail type must be one of: {', '.join(self.ALLOWED_RAIL_TYPES)}",
                    "provided_value": rail_type,
                    "allowed_values": list(self.ALLOWED_RAIL_TYPES),
                },
                status=400,
            )
        return None

    def get_base_path(self, app_type: str, rail_type: str | None = None) -> Path:
        """Get base path for application type and optional rail type."""
        path = Path("apps") / app_type
        if rail_type:
            path = path / rail_type
        return path

    def is_valid_date_dir(self, dir_name: str) -> bool:
        """Check if directory name is in valid date format (yyyy_mm_dd)."""
        try:
            parts = dir_name.split("_")
            if len(parts) != 3:
                return False

            year, month, day = parts
            if (
                len(year) == self.YEAR_LENGTH
                and len(month) == self.MONTH_DAY_LENGTH
                and len(day) == self.MONTH_DAY_LENGTH
            ):
                # Validate it's a real date
                date(int(year), int(month), int(day))
                return True
        except (ValueError, TypeError):
            pass
        return False

    def parse_date_from_dir(self, dir_name: str) -> str:
        """Parse date from directory name."""
        try:
            year, month, day = dir_name.split("_")
            return f"{year}-{month}-{day}"
        except (ValueError, TypeError):
            return dir_name

    def get_file_size(self, file_path: str) -> int | None:
        """Get file size in bytes."""
        try:
            if default_storage.exists(file_path):
                return default_storage.size(file_path)
        except Exception:
            pass
        return None

    def get_file_url(self, file_path: str) -> str:
        """Generate file URL for download."""
        return f"/media/{file_path}"

    def find_versions_for_path(
        self, base_path: Path, app_type: str, rail_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Find versions for a specific path."""
        versions = []
        app_name = self.get_app_name(app_type)

        try:
            if default_storage.exists(str(base_path)):
                dirs, _ = default_storage.listdir(str(base_path))

                for dir_name in dirs:
                    if self.is_valid_date_dir(dir_name):
                        file_path = base_path / dir_name / app_name
                        if default_storage.exists(str(file_path)):
                            version_data = {
                                "date": self.parse_date_from_dir(dir_name),
                                "date_dir": dir_name,
                                "file_path": str(file_path),
                                "file_url": self.get_file_url(str(file_path)),
                                "file_name": app_name,
                                "app_type": app_type,
                                "exists": True,
                                "size": self.get_file_size(str(file_path)),
                            }
                            if rail_type:
                                version_data["rail_type"] = rail_type
                            versions.append(version_data)
        except Exception:
            logger.exception(f"Error listing versions in {base_path}")

        # Sort by date (newest first)
        versions.sort(key=lambda x: x["date_dir"], reverse=True)
        return versions

    def find_latest_file(self, app_type: str, rail_type: str | None = None) -> dict[str, Any] | None:
        """Find the most recent application file."""
        try:
            base_path = self.get_base_path(app_type, rail_type)
            app_name = self.get_app_name(app_type)

            date_dirs = []
            if default_storage.exists(str(base_path)):
                dirs, _ = default_storage.listdir(str(base_path))
                date_dirs = [d for d in dirs if self.is_valid_date_dir(d)]

            if not date_dirs:
                return None

            date_dirs.sort(reverse=True)

            for date_dir in date_dirs:
                file_path = base_path / date_dir / app_name
                if default_storage.exists(str(file_path)):
                    return {
                        "file_path": str(file_path),
                        "file_url": self.get_file_url(str(file_path)),
                        "date": self.parse_date_from_dir(date_dir),
                        "date_dir": date_dir,
                        "app_type": app_type,
                        "rail_type": rail_type,
                        "file_name": app_name,
                    }

            return None

        except Exception as e:
            logger.exception(f"Error finding latest file for {app_type}")
            return None


@method_decorator(login_required, name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
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
        try:
            return JsonResponse(
                {
                    "status": "success",
                    "is_authenticated": request.user.is_authenticated,
                    "is_staff": request.user.is_staff,
                    "username": request.user.username if request.user.is_authenticated else None,
                }
            )
        except Exception as e:
            logger.exception("Auth check failed")
            return JsonResponse(
                {"status": "error", "error": f"Authentication check failed: {str(e)}"}, status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class AppFileUploadView(View):
    """View for uploading application .exe files.

    Handles POST requests with file upload for Kalmar32/Phasar32/ManualApp applications.
    Files are saved to media/apps/<type>/[rail_type/]<yyyy_mm_dd>/<AppName>.exe
    """

    http_method_names: ClassVar[list[str]] = ["post"]
    ALLOWED_TYPES: ClassVar[tuple[str, ...]] = ("kalmar32", "phasar32", "manual_app")
    ALLOWED_RAIL_TYPES: ClassVar[tuple[str, ...]] = ("P65", "IRS52", "UIC60")
    MAX_FILE_SIZE: ClassVar[int] = 500 * 1024 * 1024  # 500MB
    APP_NAME_MAP: ClassVar[dict[str, str]] = {
        "kalmar32": "Kalmar.exe",
        "phasar32": "Phasar.exe",
        "manual_app": "ManualApp.exe",
    }

    def post(self, request: HttpRequest) -> JsonResponse:
        """Upload application .exe file."""
        try:
            # Check authentication
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "Authentication required",
                        "detail": "You must be logged in to upload files",
                    },
                    status=401,
                )

            # Check if user has staff permissions
            if not request.user.is_staff:
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "Permission denied",
                        "detail": "Only staff members can upload application files",
                    },
                    status=403,
                )

            # Validate request has files
            if not request.FILES:
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "No file provided",
                        "detail": "Request must contain a file in multipart/form-data format",
                    },
                    status=400,
                )

            file_obj = self._get_uploaded_file(request)
            app_type = self._get_app_type(request)
            rail_type = self._get_rail_type(request, app_type)
            self._validate_file(file_obj, app_type)

            file_path = self._save_file(file_obj, app_type, rail_type)
            return self._build_success_response(file_path, app_type, rail_type)

        except ValidationError as e:
            return JsonResponse(
                {"status": "error", "error": str(e), "detail": "Validation failed for the uploaded file"},
                status=400,
            )
        except PermissionError as e:
            return JsonResponse(
                {"status": "error", "error": str(e), "detail": "Permission denied for file operation"},
                status=403,
            )
        except OSError as e:
            logger.exception("File system error during upload")
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"File system error: {str(e)}",
                    "detail": "Failed to save file to storage",
                },
                status=500,
            )
        except Exception as e:
            logger.exception("Unexpected error during file upload")
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Upload failed: {str(e)}",
                    "detail": "An unexpected error occurred during file upload",
                },
                status=500,
            )

    def _get_uploaded_file(self, request: HttpRequest) -> object:
        """Extract uploaded file from request."""
        file_obj = request.FILES.get("file")
        if not file_obj:
            msg = "File field 'file' is required"
            raise ValidationError(msg)
        return file_obj

    def _get_app_type(self, request: HttpRequest) -> str:
        """Extract and validate application type."""
        app_type = request.POST.get("type", "").lower().strip()
        if not app_type:
            msg = "Application type field 'type' is required"
            raise ValidationError(msg)

        if app_type not in self.ALLOWED_TYPES:
            msg = f"Invalid application type: '{app_type}'. Must be one of: {', '.join(self.ALLOWED_TYPES)}"
            raise ValidationError(msg)

        return app_type

    def _get_rail_type(self, request: HttpRequest, app_type: str) -> str | None:
        """Extract and validate rail type for Kalmar32."""
        if app_type != "kalmar32":
            return None

        rail_type = request.POST.get("rail_type", "").upper().strip()
        if not rail_type:
            msg = "Rail type field 'rail_type' is required for Kalmar32 applications"
            raise ValidationError(msg)

        if rail_type not in self.ALLOWED_RAIL_TYPES:
            msg = f"Invalid rail type: '{rail_type}'. Must be one of: {', '.join(self.ALLOWED_RAIL_TYPES)}"
            raise ValidationError(msg)

        return rail_type

    def _validate_file(self, file_obj: object, app_type: str) -> None:
        """Validate uploaded file."""
        # Check file extension
        if not file_obj.name.lower().endswith(".exe"):
            msg = f"Invalid file type: '{file_obj.name}'. Only .exe files are allowed"
            raise ValidationError(msg)

        # Check file size
        if file_obj.size > self.MAX_FILE_SIZE:
            msg = f"File size ({file_obj.size} bytes) exceeds maximum allowed size of {self.MAX_FILE_SIZE} bytes"
            raise ValidationError(msg)

        # Validate file name based on type
        expected_name = self.APP_NAME_MAP.get(app_type)

        if file_obj.name != expected_name:
            logger.warning(
                "File name '%s' doesn't match expected name '%s' for type '%s'",
                file_obj.name,
                expected_name,
                app_type,
            )
            # Don't raise ValidationError, just warn

    def _save_file(self, file_obj: object, app_type: str, rail_type: str | None = None) -> str:
        """Save file to media storage."""
        try:
            today = timezone.now().date()
            date_str = today.strftime("%Y_%m_%d")

            # Get file name based on app type
            file_name = self.APP_NAME_MAP.get(app_type)

            # Build file path based on app type
            if app_type == "kalmar32" and rail_type:
                file_path = f"apps/{app_type}/{rail_type}/{date_str}/{file_name}"
            else:
                file_path = f"apps/{app_type}/{date_str}/{file_name}"

            # Delete existing file if it exists
            if default_storage.exists(file_path):
                logger.info(f"Deleting existing file: {file_path}")
                default_storage.delete(file_path)

            # Save new file
            saved_path = default_storage.save(file_path, file_obj)
            logger.info(f"File saved successfully: {saved_path}")
            return saved_path

        except Exception as e:
            logger.exception(f"Failed to save file: {str(e)}")
            raise

    def _build_success_response(
        self, file_path: str, app_type: str, rail_type: str | None = None
    ) -> JsonResponse:
        """Build success response."""
        response_data = {
            "status": "success",
            "message": "File uploaded successfully",
            "file_path": file_path,
            "app_type": app_type,
            "upload_date": timezone.now().date().isoformat(),
            "file_url": f"/media/{file_path}",
            "uploaded_by": "staff",
        }

        if rail_type:
            response_data["rail_type"] = rail_type

        return JsonResponse(response_data, status=201)


class AppFileDownloadView(BaseAppVersionView):
    """View for retrieving the latest application .exe file.

    Handles GET requests to download the most recent version of the application.
    """

    http_method_names: ClassVar[list[str]] = ["get"]

    @property
    def app_name_map(self) -> dict[str, str]:
        return {
            "kalmar32": "Kalmar.exe",
            "phasar32": "Phasar.exe",
            "manual_app": "ManualApp.exe",
        }

    def get(self, request: HttpRequest, app_type: str) -> FileResponse | JsonResponse:
        """Get the latest application .exe file."""
        try:
            # Validate application type
            error_response = self.validate_app_type(app_type)
            if error_response:
                return error_response

            # Get rail_type parameter for Kalmar32
            rail_type = None
            if app_type == "kalmar32":
                rail_type = request.GET.get("rail_type", "").upper().strip()

                if not rail_type:
                    return JsonResponse(
                        {
                            "status": "error",
                            "error": "Missing rail_type parameter",
                            "detail": "Rail type parameter 'rail_type' is required for Kalmar32 applications",
                            "required_parameter": "rail_type",
                            "allowed_values": list(self.ALLOWED_RAIL_TYPES),
                        },
                        status=400,
                    )

                error_response = self.validate_rail_type(rail_type)
                if error_response:
                    return error_response

            # Find latest file
            file_info = self.find_latest_file(app_type, rail_type)

            if not file_info:
                path_description = f"apps/{app_type}"
                if rail_type:
                    path_description += f"/{rail_type}"

                return JsonResponse(
                    {
                        "status": "error",
                        "error": "No application file found",
                        "detail": f"No {app_type} application file found in {path_description}",
                        "app_type": app_type,
                        "rail_type": rail_type,
                        "suggestion": "Upload a file first using the upload endpoint",
                    },
                    status=404,
                )

            # Check if file exists in storage
            if not default_storage.exists(file_info["file_path"]):
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "File not found in storage",
                        "detail": f"The file {file_info['file_path']} exists in database but not in storage",
                        "file_path": file_info["file_path"],
                    },
                    status=404,
                )

            # Open and return the file
            try:
                file = default_storage.open(file_info["file_path"], "rb")
                file_name = Path(file_info["file_path"]).name

                response = FileResponse(
                    file,
                    as_attachment=True,
                    filename=file_name,
                    content_type="application/octet-stream",
                )

                # Add custom headers
                response["Content-Disposition"] = f'attachment; filename="{file_name}"'
                response["X-App-Type"] = app_type
                if rail_type:
                    response["X-Rail-Type"] = rail_type
                response["X-File-Date"] = file_info.get("date", "")

                return response

            except Exception as e:
                logger.exception(f"Failed to open file: {file_info['file_path']}")
                return JsonResponse(
                    {
                        "status": "error",
                        "error": f"Failed to read file: {str(e)}",
                        "detail": "The file exists but cannot be opened",
                        "file_path": file_info["file_path"],
                    },
                    status=500,
                )

        except Exception as e:
            logger.exception("Unexpected error during file download")
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Download failed: {str(e)}",
                    "detail": "An unexpected error occurred during file download",
                },
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class AppFileListVersionsView(BaseAppVersionView):
    """View for listing all available versions of an application."""

    http_method_names: ClassVar[list[str]] = ["get"]

    @property
    def app_name_map(self) -> dict[str, str]:
        return {
            "kalmar32": "Kalmar.exe",
            "phasar32": "Phasar.exe",
            "manual_app": "ManualApp.exe",
        }

    def get(self, request: HttpRequest, app_type: str) -> JsonResponse:
        """Get list of all available application versions."""
        try:
            # Validate application type
            error_response = self.validate_app_type(app_type)
            if error_response:
                return error_response

            # Get rail_type parameter for Kalmar32
            rail_type = None
            if app_type == "kalmar32":
                rail_type = request.GET.get("rail_type", "").upper().strip()

                error_response = self.validate_rail_type(rail_type)
                if error_response:
                    return error_response

            # Find all versions
            versions = self._find_all_versions(app_type, rail_type)

            response_data = {
                "status": "success",
                "app_type": app_type,
                "total_versions": len(versions),
                "versions": versions,
            }

            if rail_type:
                response_data["rail_type"] = rail_type
                response_data["filtered_by_rail"] = True
            else:
                response_data["filtered_by_rail"] = False

            if versions:
                response_data["latest"] = versions[0]
                response_data["oldest"] = versions[-1]

            return JsonResponse(response_data, status=200)

        except Exception as e:
            logger.exception("Unexpected error during versions list")
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Failed to list versions: {e!s}",
                    "detail": "An unexpected error occurred while listing versions",
                },
                status=500,
            )

    def _find_all_versions(self, app_type: str, rail_type: str | None = None) -> list[dict[str, Any]]:
        """Find all available versions of the application."""
        try:
            if rail_type:
                # Specific rail type requested
                base_path = self.get_base_path(app_type, rail_type)
                return self.find_versions_for_path(base_path, app_type, rail_type)
            elif app_type == "kalmar32":
                # No rail type specified for Kalmar32 - search all rail types
                return self._find_all_versions_all_rails(app_type)
            else:
                # Non-Kalmar32 app without rail type
                base_path = self.get_base_path(app_type)
                return self.find_versions_for_path(base_path, app_type, None)

        except Exception:
            logger.exception(f"Error finding versions for {app_type}")
            return []

    def _find_all_versions_all_rails(self, app_type: str) -> list[dict[str, Any]]:
        """Find all versions for Kalmar32 across all rail types."""
        versions = []
        base_path = Path("apps") / app_type

        try:
            if default_storage.exists(str(base_path)):
                # Get all rail type directories
                rail_dirs, _ = default_storage.listdir(str(base_path))

                for rail_dir in rail_dirs:
                    if rail_dir in self.ALLOWED_RAIL_TYPES:
                        rail_versions = self.find_versions_for_path(base_path / rail_dir, app_type, rail_dir)
                        versions.extend(rail_versions)
        except Exception:
            logger.exception("Error listing versions for all rail types")

        # Sort by date (newest first)
        versions.sort(key=lambda x: (x["date_dir"], x.get("rail_type", "")), reverse=True)
        return versions


@method_decorator(csrf_exempt, name="dispatch")
class AppFileLatestVersionDateView(BaseAppVersionView):
    """View for getting the date of the latest application version."""

    http_method_names: ClassVar[list[str]] = ["get"]

    @property
    def app_name_map(self) -> dict[str, str]:
        return {
            "kalmar32": "Kalmar.exe",
            "phasar32": "Phasar.exe",
            "manual_app": "ManualApp.exe",
        }

    def get(self, request: HttpRequest, app_type: str) -> JsonResponse:
        """Get the date of the latest application version."""
        try:
            # Validate application type
            error_response = self.validate_app_type(app_type)
            if error_response:
                return error_response

            # Get rail_type parameter for Kalmar32
            rail_type = None
            if app_type == "kalmar32":
                rail_type = request.GET.get("rail_type", "").upper().strip()

                error_response = self.validate_rail_type(rail_type)
                if error_response:
                    return error_response

            # Find latest file using base class method
            file_info = self.find_latest_file(app_type, rail_type if rail_type else None)

            if not file_info:
                path_description = f"apps/{app_type}"
                if rail_type:
                    path_description += f"/{rail_type}"

                return JsonResponse(
                    {
                        "status": "error",
                        "error": "No application file found",
                        "detail": f"No {app_type} application file found in {path_description}",
                        "app_type": app_type,
                        "rail_type": rail_type,
                    },
                    status=404,
                )

            # Build response
            response_data = {
                "status": "success",
                "app_type": app_type,
                "date": file_info["date"],
                "date_dir": file_info["date_dir"],
                "file_name": file_info["file_name"],
                "file_exists": default_storage.exists(file_info["file_path"]),
            }

            if rail_type:
                response_data["rail_type"] = rail_type
            elif app_type == "kalmar32" and "rail_type" in file_info:
                response_data["rail_type"] = file_info["rail_type"]

            # Add file size if file exists
            if response_data["file_exists"]:
                with contextlib.suppress(Exception):
                    response_data["file_size"] = default_storage.size(file_info["file_path"])

            return JsonResponse(response_data, status=200)

        except Exception as e:
            logger.exception("Unexpected error getting latest version date")
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Failed to get latest version date: {e!s}",
                },
                status=500,
            )
