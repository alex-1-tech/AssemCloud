"""License model for managing Kalmar32 equipment licenses.

This module provides the License model for storing and managing
license information including version, product details, hardware IDs,
expiration dates, and digital signatures.
"""
import base64
import json
from datetime import date
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class License(models.Model):
    """License for Kalmar32 equipment."""

    ver = models.CharField(
        _("License version"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("Version of the license key"),
    )

    product = models.CharField(
        _("Product"),
        max_length=100,
        help_text=_("Product name"),
    )

    company_name = models.CharField(
        _("Company name"),
        max_length=200,
        blank=True,
        default="",
        help_text=_("Company name"),
    )

    host_hwid = models.CharField(
        _("Host HWID"),
        max_length=150,
        help_text=_("Hardware ID of the host"),
    )

    device_hwid = models.CharField(
        _("Device HWID"),
        max_length=150,
        blank=True,
        default="",
        help_text=_("Hardware ID of the device"),
    )

    exp = models.DateField(
        _("Expiration date"),
        default=date(2100, 1, 1),
        help_text=_("Expiration date of the license"),
    )

    features = models.JSONField(
        _("Features"),
        default=dict,
        help_text=_("Additional features in JSON format"),
    )

    signature = models.TextField(
        _("Signature"),
        blank=True,
        help_text=_("Digital signature of the license"),
    )

    license_key = models.TextField(
        _("License key"),
        help_text=_("Generated license key in base64url(payload).base64url(signature) format"),
    )

    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
        help_text=_("Creation date of the license"),
    )

    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
        help_text=_("Last update date of the license"),
    )

    class Meta:
        """Meta options for License model."""

        verbose_name = _("License")
        verbose_name_plural = _("Licenses")
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of the object."""
        return "License"

    def get_license_payload(self) -> dict:
        """Get payload of the license as a dictionary."""
        return {
            "ver": self.ver,
            "product": self.product,
            "company_name": self.company_name,
            "host_hwid": self.host_hwid,
            "device_hwid": self.device_hwid,
            "exp": self.exp.isoformat() if self.exp else "2100-01-01",
            "features": self.features,
        }

    def generate_license_key(self, signature_bytes: bytes) -> str:
        """Generate license key in base64url(payload).base64url(signature) format."""
        payload_json = json.dumps(self.get_license_payload(), separators=(",", ":"))
        payload_bytes = payload_json.encode("utf-8")

        def to_base64url(data_bytes: bytes) -> str:
            """Convert base64 to base64url."""
            return (
                base64.b64encode(data_bytes).decode("utf-8").replace("+", "-").replace("/", "_").rstrip("=")
            )

        payload_b64 = to_base64url(payload_bytes)
        signature_b64 = to_base64url(signature_bytes)

        return f"{payload_b64}.{signature_b64}"

    def clean(self) -> None:
        """Additional validation of the model."""
        super().clean()
        self._validate_exp_date()

    def _validate_exp_date(self) -> None:
        """Validate expiration date."""
        if self.exp and self.exp < timezone.now().date():
            raise ValidationError(
                _("Expiration date cannot be in the past"),
            )
