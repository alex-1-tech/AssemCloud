import base64
import json
from datetime import date
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class License(models.Model):
    """Лицензия для оборудования Kalmar32."""

    ver = models.CharField(
        _("Версия лицензии"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("Версия лицензионного ключа"),
    )

    product = models.CharField(
        _("Продукт"),
        max_length=100,
        help_text=_("Название продукта"),
    )

    company_name = models.CharField(
        _("Название компании"),
        max_length=200,
        blank=True,
        default="",
        help_text=_("Название компании="),
    )

    host_hwid = models.CharField(
        _("Host HWID"),
        max_length=150,
        help_text=_("Hardware ID хоста"),
    )

    device_hwid = models.CharField(
        _("Device HWID"),
        max_length=150,
        blank=True,
        default="",
        help_text=_("Hardware ID устройства"),
    )

    exp = models.DateField(
        _("Дата истечения"),
        default=date(2100, 1, 1),
        help_text=_("Дата истечения срока действия лицензии"),
    )

    features = models.JSONField(
        _("Функциональность"),
        default=dict,
        help_text=_("Дополнительные функции в формате JSON"),
    )

    signature = models.TextField(
        _("Подпись"),
        blank=True,
        help_text=_("Цифровая подпись лицензии"),
    )

    license_key = models.TextField(
        _("Лицензионный ключ"),
        help_text=_(
            "Сгенерированный лицензионный ключ\
                 в формате base64url(payload).base64url(signature)"
        ),
    )

    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
        help_text=_("Дата создания лицензии"),
    )

    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
        help_text=_("Дата последнего обновления лицензии"),
    )

    class Meta:
        """Meta options for License model."""

        verbose_name = _("Лицензия")
        verbose_name_plural = _("Лицензии")
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of the object."""
        return "Лицензия"

    def get_license_payload(self) -> dict:
        """Получить payload лицензии в виде словаря."""
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
        """Генерация licenseKey в формате base64url(payload).base64url(signature)."""
        payload_json = json.dumps(self.get_license_payload(), separators=(",", ":"))
        payload_bytes = payload_json.encode("utf-8")

        def to_base64url(data_bytes: bytes) -> str:
            """Конвертация base64 в base64url."""
            return (
                base64.b64encode(data_bytes)
                .decode("utf-8")
                .replace("+", "-")
                .replace("/", "_")
                .rstrip("=")
            )

        payload_b64 = to_base64url(payload_bytes)
        signature_b64 = to_base64url(signature_bytes)

        return f"{payload_b64}.{signature_b64}"

    def clean(self) -> None:
        """Дополнительная валидация модели."""
        super().clean()
        self._validate_exp_date()

    def _validate_exp_date(self) -> None:
        """Проверка даты истечения срока действия."""
        if self.exp and self.exp < timezone.now().date():
            raise ValidationError(
                _("Дата истечения срока действия не может быть в прошлом"),
            )
