"""API views for application file management (universal).

Supports any application type (app_type), optional rail_type and version.
Files are stored as: apps/<app_type>/<version>/[<rail_type>/]<YYYY_MM_DD>/<original_filename>.exe
"""

from __future__ import annotations

import json
import logging
import os
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import Model, RailType

logger = logging.getLogger(__name__)
MANUAL_APP_TYPE = "manual_app"


class BaseAppVersionView(View):
    """Base class with common file operations (supports version)."""

    DATE_PARTS_COUNT = 3
    YEAR_LENGTH = 4
    MONTH_DAY_LENGTH = 2

    @staticmethod
    def get_base_path(app_type: str, version: str, rail_type: str | None = None) -> Path:
        """Build base path: apps/<app_type>/<version>[/<rail_type>]."""
        path = Path("apps") / app_type / version
        if rail_type:
            path = path / rail_type
        return path

    @staticmethod
    def is_valid_date_dir(dir_name: str) -> bool:
        """Check if directory name matches YYYY_MM_DD."""
        try:
            parts = dir_name.split("_")
            if len(parts) != 3:
                return False
            year, month, day = parts
            if len(year) == 4 and len(month) == 2 and len(day) == 2:
                date(int(year), int(month), int(day))
                return True
        except (ValueError, TypeError):
            pass
        return False

    @staticmethod
    def parse_date_from_dir(dir_name: str) -> str:
        """Convert YYYY_MM_DD to YYYY-MM-DD."""
        try:
            y, m, d = dir_name.split("_")
            return f"{y}-{m}-{d}"
        except ValueError:
            return dir_name

    @staticmethod
    def get_file_size(file_path: str) -> int | None:
        try:
            if default_storage.exists(file_path):
                return default_storage.size(file_path)
        except OSError:
            pass
        return None

    @staticmethod
    def get_file_url(file_path: str) -> str:
        return f"/media/{file_path}"

    @classmethod
    def find_versions(
        cls,
        app_type: str,
        version: str,
        rail_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Find all version directories and return info about .exe files found.
        Returns list sorted by date descending.
        """
        base_path = cls.get_base_path(app_type, rail_type, version)
        versions = []

        try:
            if default_storage.exists(str(base_path)):
                dirs, _ = default_storage.listdir(str(base_path))
                date_dirs = [d for d in dirs if cls.is_valid_date_dir(d)]

                for date_dir in date_dirs:
                    sub_path = base_path / date_dir
                    full_sub = Path(settings.MEDIA_ROOT) / sub_path
                    if full_sub.is_dir():
                        files_in_dir, _ = default_storage.listdir(str(sub_path))
                        exe_files = [
                            f.name
                            for f in full_sub.iterdir()
                            if f.is_file() and f.name.lower().endswith(".exe")
                        ]
                        if exe_files:
                            exe_name = exe_files[0]
                            file_path = str(sub_path / exe_name)
                            versions.append(
                                {
                                    "date": cls.parse_date_from_dir(date_dir),
                                    "date_dir": date_dir,
                                    "file_path": file_path,
                                    "file_url": cls.get_file_url(file_path),
                                    "file_name": exe_name,
                                    "app_type": app_type,
                                    "version": version,
                                    "rail_type": rail_type,
                                    "size": cls.get_file_size(file_path),
                                    "exists": True,
                                }
                            )
        except Exception:
            logger.exception("Error listing versions for %s version %s", app_type, version)

        versions.sort(key=lambda x: x["date_dir"], reverse=True)
        return versions

    @classmethod
    def find_latest(
        cls,
        app_type: str,
        version: str,
        rail_type: str | None = None,
    ) -> dict[str, Any] | None:
        """Return the most recent version info or None."""
        versions = cls.find_versions(app_type, version, rail_type)
        return versions[0] if versions else None


@method_decorator(login_required, name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
class AppUploadPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        models_by_name = defaultdict(list)
        for m in Model.objects.all():
            models_by_name[m.name].append(m)

        app_types = []
        for name, models in models_by_name.items():
            rail_types = set()
            versions_by_rail = defaultdict(set)
            for m in models:
                rail = m.type_rail
                rail_types.add(rail)
                versions_by_rail[rail].add(m.version)

            versions_by_rail = {k: sorted(v) for k, v in versions_by_rail.items()}

            rail_options = []
            for rail in sorted(rail_types):
                if rail != "NONE":
                    label = dict(RailType.choices).get(rail, rail)
                    rail_options.append({"value": rail, "label": label})

            rail_required = any(rail != "NONE" for rail in rail_types)

            app_types.append(
                {
                    "value": name,
                    "label": name.capitalize(),
                    "rail_required": rail_required,
                    "rail_types": rail_options,
                    "versions_by_rail_json": json.dumps(versions_by_rail),
                }
            )

        app_types.append(
            {
                "value": MANUAL_APP_TYPE,
                "label": "Manual App",
                "rail_required": False,
                "rail_types": [],
                "versions_by_rail_json": "{}",
            }
        )

        context = {
            "user": request.user,
            "app_types": app_types,
        }
        return render(request, "app_upload.html", context)


class AuthCheckView(View):
    """Check authentication status."""

    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse(
            {
                "status": "success",
                "is_authenticated": request.user.is_authenticated,
                "is_staff": request.user.is_staff,
                "username": request.user.username if request.user.is_authenticated else None,
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class AppFileUploadView(View):
    """Upload an .exe file for any application type, with version and optional rail_type."""

    http_method_names = ["post"]
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

    def post(self, request: HttpRequest) -> JsonResponse:
        if not request.user.is_authenticated:
            return self._error("Authentication required", status=401)
        if not request.user.is_staff:
            return self._error("Permission denied", status=403)

        if not request.FILES:
            return self._error("No file provided", status=400)

        file_obj = request.FILES.get("file")
        if not file_obj:
            return self._error("File field 'file' is required", status=400)

        app_type = request.POST.get("type", "").strip()
        if not app_type:
            return self._error("Application type 'type' is required", status=400)
        if not re.match(r"^[a-zA-Z0-9_\-]+$", app_type):
            return self._error("Invalid app_type format", status=400)

        is_manual = app_type == MANUAL_APP_TYPE  # NEW

        if not is_manual:
            version = request.POST.get("version", "").strip()
            if not version:
                return self._error("Version 'version' is required for this app type", status=400)
            if not re.match(r"^[a-zA-Z0-9_\-\.]+$", version):
                return self._error("Invalid version format", status=400)
            rail_type = request.POST.get("rail_type", "").strip()
            if rail_type and not re.match(r"^[a-zA-Z0-9_\-]+$", rail_type):
                return self._error("Invalid rail_type format", status=400)
            rail_type = rail_type or None

            if not Model.objects.filter(
                name=app_type, version=version, type_rail=rail_type or "NONE"
            ).exists():
                return self._error("Invalid combination: no such model variant", status=400)
        else:
            version = None
            rail_type = None

        if not file_obj.name.lower().endswith(".exe"):
            return self._error("Only .exe files are allowed", status=400)

        if file_obj.size > self.MAX_FILE_SIZE:
            return self._error(f"File exceeds {self.MAX_FILE_SIZE // (1024 * 1024)} MB limit", status=400)

        original_name = file_obj.name
        today = timezone.now().date().strftime("%Y_%m_%d")

        # Формируем путь
        if is_manual:
            base_path = Path("apps") / MANUAL_APP_TYPE
        else:
            base_path = Path("apps") / app_type
            if rail_type:
                base_path = base_path / rail_type
            base_path = base_path / version

        date_path = base_path / today
        full_path = str(date_path / original_name)

        if default_storage.exists(full_path):
            default_storage.delete(full_path)

        saved_path = default_storage.save(full_path, file_obj)

        response = {
            "status": "success",
            "message": "File uploaded successfully",
            "file_path": saved_path,
            "file_url": f"/media/{saved_path}",
            "app_type": app_type,
            "upload_date": timezone.now().date().isoformat(),
        }
        if not is_manual:
            response["version"] = version
            response["rail_type"] = rail_type

        return JsonResponse(response, status=201)

    def _error(self, message: str, status: int = 400) -> JsonResponse:
        return JsonResponse({"status": "error", "error": message}, status=status)


class AppFileDownloadView(BaseAppVersionView):
    """Download the latest version of an application file for given app_type, version and optional rail_type."""

    http_method_names = ["get"]

    def get(self, request: HttpRequest, app_type: str) -> FileResponse | JsonResponse:
        is_manual = app_type == MANUAL_APP_TYPE

        if is_manual:
            base = Path("apps") / MANUAL_APP_TYPE
            try:
                if default_storage.exists(str(base)):
                    dirs, _ = default_storage.listdir(str(base))
                    date_dirs = sorted([d for d in dirs if self.is_valid_date_dir(d)], reverse=True)
                    for date_dir in date_dirs:
                        sub_path = base / date_dir
                        full_sub = Path(settings.MEDIA_ROOT) / sub_path
                        if full_sub.is_dir():
                            exe_files = [
                                f.name
                                for f in full_sub.iterdir()
                                if f.is_file() and f.name.lower().endswith(".exe")
                            ]
                            if exe_files:
                                exe_name = exe_files[0]
                                file_path = str(sub_path / exe_name)
                                file_info = {
                                    "file_path": file_path,
                                    "file_name": exe_name,
                                    "date": self.parse_date_from_dir(date_dir),
                                }
                                return self._serve_file(file_info, app_type)
            except Exception:
                logger.exception("Error listing manual app files")
            return self._error("No manual application file found", status=404)

        # Обычная логика с версией и рельсом
        version = request.GET.get("version", "").strip()
        if not version:
            return self._error("Version parameter is required", status=400)
        rail_type = request.GET.get("rail_type", "").strip() or None

        if not re.match(r"^[a-zA-Z0-9_\-]+$", app_type):
            return self._error("Invalid app_type", status=400)
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", version):
            return self._error("Invalid version format", status=400)
        if rail_type and not re.match(r"^[a-zA-Z0-9_\-]+$", rail_type):
            return self._error("Invalid rail_type", status=400)

        file_info = self.find_latest(app_type, version, rail_type)
        if not file_info:
            return self._error("No application file found", status=404)

        return self._serve_file(file_info, app_type)

    def _serve_file(self, file_info: dict, app_type: str) -> FileResponse | JsonResponse:
        """Общий метод для отдачи файла."""
        file_path = file_info["file_path"]
        if not default_storage.exists(file_path):
            return self._error("File not found in storage", status=404)

        try:
            file_handle = default_storage.open(file_path, "rb")
            response = FileResponse(
                file_handle,
                as_attachment=True,
                filename=file_info["file_name"],
                content_type="application/octet-stream",
            )
            response["Content-Disposition"] = f'attachment; filename="{file_info["file_name"]}"'
            response["X-App-Type"] = app_type
            if "version" in file_info:
                response["X-Version"] = file_info["version"]
            if "rail_type" in file_info:
                response["X-Rail-Type"] = file_info["rail_type"]
            response["X-File-Date"] = file_info["date"]
            return response
        except Exception as e:
            logger.exception("Failed to open file: %s", file_path)
            return self._error(f"Failed to read file: {e!s}", status=500)

    def _error(self, message: str, status: int = 400) -> JsonResponse:
        return JsonResponse({"status": "error", "error": message}, status=status)


@method_decorator(csrf_exempt, name="dispatch")
class AppFileListVersionsView(BaseAppVersionView):
    """List all versions for a given app_type, version (optionally filtered by rail_type)."""

    http_method_names = ["get"]

    def get(self, request: HttpRequest, app_type: str) -> JsonResponse:
        version = request.GET.get("version", "").strip()
        if not version:
            return self._error("Version parameter is required", status=400)
        rail_type = request.GET.get("rail_type", "").strip() or None

        if not re.match(r"^[a-zA-Z0-9_\-]+$", app_type):
            return self._error("Invalid app_type", status=400)
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", version):
            return self._error("Invalid version format", status=400)
        if rail_type and not re.match(r"^[a-zA-Z0-9_\-]+$", rail_type):
            return self._error("Invalid rail_type", status=400)

        if app_type.lower() == "kalmar32" and not rail_type:
            base = self.get_base_path(app_type, version)
            versions = []
            try:
                if default_storage.exists(str(base)):
                    items, _ = default_storage.listdir(str(base))
                    for item in items:
                        if self.is_valid_date_dir(item):
                            continue
                        sub_versions = self.find_versions(app_type, version, item)
                        versions.extend(sub_versions)
            except Exception:
                logger.exception("Error scanning kalmar32 rail types for version %s", version)
            versions.sort(key=lambda x: x["date_dir"], reverse=True)
        else:
            versions = self.find_versions(app_type, version, rail_type)

        response = {
            "status": "success",
            "app_type": app_type,
            "version": version,
            "total_versions": len(versions),
            "versions": versions,
        }
        if rail_type:
            response["rail_type"] = rail_type
        return JsonResponse(response, status=200)

    def _error(self, message: str, status: int = 400) -> JsonResponse:
        return JsonResponse({"status": "error", "error": message}, status=status)


@method_decorator(csrf_exempt, name="dispatch")
class AppFileLatestVersionDateView(BaseAppVersionView):
    """Return the date of the latest version for given app_type, version and optional rail_type."""

    http_method_names = ["get"]

    def get(self, request: HttpRequest, app_type: str) -> JsonResponse:
        if app_type == MANUAL_APP_TYPE:
            base = Path("apps") / MANUAL_APP_TYPE
            try:
                if default_storage.exists(str(base)):
                    dirs, _ = default_storage.listdir(str(base))
                    date_dirs = sorted([d for d in dirs if self.is_valid_date_dir(d)], reverse=True)
                    for date_dir in date_dirs:
                        sub_path = base / date_dir
                        full_sub = Path(settings.MEDIA_ROOT) / sub_path
                        if full_sub.is_dir():
                            exe_files = [
                                f.name
                                for f in full_sub.iterdir()
                                if f.is_file() and f.name.lower().endswith(".exe")
                            ]
                            if exe_files:
                                return JsonResponse(
                                    {
                                        "status": "success",
                                        "app_type": app_type,
                                        "date": self.parse_date_from_dir(date_dir),
                                        "date_dir": date_dir,
                                        "file_name": exe_files[0],
                                        "file_exists": True,
                                    }
                                )
            except Exception:
                logger.exception("Error listing manual app files")
            return self._error("No manual application file found", status=404)
        version = request.GET.get("version", "").strip()
        if not version:
            return self._error("Version parameter is required", status=400)
        rail_type = request.GET.get("rail_type", "").strip() or None

        if not re.match(r"^[a-zA-Z0-9_\-]+$", app_type):
            return self._error("Invalid app_type", status=400)
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", version):
            return self._error("Invalid version format", status=400)
        if rail_type and not re.match(r"^[a-zA-Z0-9_\-]+$", rail_type):
            return self._error("Invalid rail_type", status=400)

        file_info = self.find_latest(app_type, version, rail_type)
        if not file_info:
            return self._error("No file found", status=404)

        response = {
            "status": "success",
            "app_type": app_type,
            "version": version,
            "date": file_info["date"],
            "date_dir": file_info["date_dir"],
            "file_name": file_info["file_name"],
            "file_exists": default_storage.exists(file_info["file_path"]),
        }
        if rail_type:
            response["rail_type"] = rail_type
        return JsonResponse(response, status=200)

    def _error(self, message: str, status: int = 400) -> JsonResponse:
        return JsonResponse({"status": "error", "error": message}, status=status)
