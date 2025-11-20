"""Webhook view for downloading and saving application files from URLs."""

import json
import logging
import re
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import urlparse

import requests
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class AppWebhookDownloadView(View):
    """View for downloading application .exe files from URLs via webhook.

    Handles POST requests with URL to download and save Kalmar32/Phasar32 applications.
    Files are saved to media/apps/<type>/<yyyy_mm_dd>/<AppName>.exe
    """

    http_method_names: ClassVar[list[str]] = ["post"]
    ALLOWED_TYPES: ClassVar[tuple[str, ...]] = ("kalmar32", "phasar32")
    MAX_FILE_SIZE: ClassVar[int] = 500 * 1024 * 1024  # 500MB
    TIMEOUT: ClassVar[int] = 30  # seconds

    def post(self, request: HttpRequest) -> JsonResponse:
        """Download and save application .exe file from URL."""
        try:
            data = self._extract_request_data(request)
            download_url = data["url"]
            app_type = data["type"]

            self._validate_url(download_url)
            self._validate_app_type(app_type)

            file_content, file_name = self._download_file(download_url, app_type)
            file_path = self._save_file(file_content, file_name, app_type)

            return self._build_success_response(file_path, app_type, download_url)

        except ValidationError as e:
            return self._build_error_response(str(e), status=400)
        except requests.RequestException as e:
            logger.exception("File download failed from URL")
            return self._build_error_response(f"Download failed: {e}", status=400)
        except Exception as e:
            logger.exception("Webhook file processing failed")
            return self._build_error_response(str(e), status=500)

    def _extract_request_data(self, request: HttpRequest) -> dict[str, Any]:
        """Extract and validate request data."""
        try:
            data = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            msg = f"Invalid JSON data: {e}"
            raise ValidationError(msg) from e

        if not data.get("url"):
            msg = "URL field is required"
            raise ValidationError(msg)

        if not data.get("type"):
            msg = "Type field is required"
            raise ValidationError(msg)

        return data

    def _validate_url(self, url: str) -> None:
        """Validate download URL."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                msg = "URL must use HTTP or HTTPS protocol"
                raise ValidationError(msg)
        except Exception as e:
            msg = f"Invalid URL: {e}"
            raise ValidationError(msg) from e

    def _validate_app_type(self, app_type: str) -> None:
        """Validate application type."""
        if app_type not in self.ALLOWED_TYPES:
            msg = f"Type must be one of: {', '.join(self.ALLOWED_TYPES)}"
            raise ValidationError(msg)
    def _validate_file_content(self, content: bytes, file_name: str) -> None:
        """Validate downloaded file content."""
        # Check minimum size (typical PE header size)
        if len(content) < 64:
            msg = "File is too small to be a valid executable"
            raise ValidationError(msg)
        
        # Check for PE header (DOS header magic)
        if not content.startswith(b'MZ'):
            msg = "File does not appear to be a valid Windows executable (missing MZ header)"
            raise ValidationError(msg)
        
        # Check file extension
        if not file_name.lower().endswith('.exe'):
            msg = "File must have .exe extension"
            raise ValidationError(msg)
    def _download_file(self, url: str, app_type: str) -> tuple[bytes, str]:
        """Download file from URL."""
        try:
            response = requests.get(
                url,
                timeout=self.TIMEOUT,
                stream=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith(
                "application/"
            ) and not content_type.startswith("application/octet-stream"):
                logger.warning("Unexpected content type: %s", content_type)

            # Check file size
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.MAX_FILE_SIZE:
                msg = f"File size exceeds maximum of {self.MAX_FILE_SIZE} bytes"
                raise ValidationError(msg)

            # Download content
            content = response.content

            # Validate actual size
            if len(content) > self.MAX_FILE_SIZE:
                msg = f"Downloaded file size exceeds maximum of {self.MAX_FILE_SIZE} bytes"
                raise ValidationError(msg)

            # Determine file name
            file_name = self._get_file_name_from_url(url, app_type, response)
            self._validate_file_content(content, file_name)
            return content, file_name

        except requests.Timeout:
            msg = "Download timeout"
            raise ValidationError(msg) from None
        except requests.TooManyRedirects:
            msg = "Too many redirects"
            raise ValidationError(msg) from None

    def _get_file_name_from_url(
        self, url: str, app_type: str, response: requests.Response
    ) -> str:
        """Extract or generate appropriate file name."""
        # Try to get filename from Content-Disposition header
        content_disposition = response.headers.get("content-disposition", "")
        if "filename=" in content_disposition:
            filename_match = re.findall("filename=(.+)", content_disposition)
            if filename_match:
                filename = filename_match[0].strip("\"'")
                if filename.lower().endswith(".exe"):
                    return filename

        # Try to get filename from URL path
        parsed_url = urlparse(url)
        url_path = Path(parsed_url.path)
        if url_path.suffix.lower() == ".exe" and url_path.name:
            return url_path.name

        # Fallback to default name based on app type
        return "Kalmar.exe" if app_type == "kalmar32" else "Phasar.exe"

    def _save_file(self, file_content: bytes, file_name: str, app_type: str) -> str:
        """Save file content to media storage."""
        today = timezone.now().date()
        date_str = today.strftime("%Y_%m_%d")

        # Validate file name
        expected_name = "Kalmar.exe" if app_type == "kalmar32" else "Phasar.exe"
        if file_name != expected_name:
            logger.warning(
                "File name %s doesn't match expected name %s for type %s",
                file_name,
                expected_name,
                app_type,
            )

        # Build file path: apps/<type>/<yyyy_mm_dd>/<FileName>.exe
        file_path = f"apps/{app_type}/{date_str}/{file_name}"

        # Convert bytes to file-like object and save
        from django.core.files.base import ContentFile

        file_obj = ContentFile(file_content, name=file_name)

        saved_path = default_storage.save(file_path, file_obj)
        logger.info("File saved successfully: %s", saved_path)

        return saved_path
    
    def _build_success_response(
        self, file_path: str, app_type: str, download_url: str
    ) -> JsonResponse:
        """Build success response."""
        response_data = {
            "status": "success",
            "message": "File downloaded and saved successfully",
            "file_path": file_path,
            "app_type": app_type,
            "source_url": download_url,
            "download_date": timezone.now().date().isoformat(),
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
        logger.error("Webhook download error: %s - %s", message, detail)
        return JsonResponse(response_data, status=status)
