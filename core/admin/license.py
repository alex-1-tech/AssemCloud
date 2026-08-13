from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.models import License


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    """Admin configuration for managing Licenses."""

    list_display = (
        "product",
        "license_short_key",
        "host_hwid",
        "device_hwid",
        "exp",
        "linked_equipment",
        "created_at",
    )
    list_filter = (
        "product",
        "exp",
        "created_at",
    )
    search_fields = (
        "license_key",
        "host_hwid",
        "device_hwid",
        "product",
        "company_name",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        (
            _("Main Information"),
            {
                "fields": (
                    "product",
                    "ver",
                    "company_name",
                    "exp",
                ),
            },
        ),
        (
            _("Hardware Identifiers"),
            {
                "fields": (
                    "host_hwid",
                    "device_hwid",
                ),
            },
        ),
        (
            _("Functionality"),
            {
                "fields": ("features",),
            },
        ),
        (
            _("Technical Data"),
            {
                "fields": (
                    "signature",
                    "license_key",
                ),
            },
        ),
        (
            _("Dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "license_key",
        "signature",
    )

    @admin.display(description=_("License Key"))
    def license_short_key(self, obj: License) -> str:
        """Display short version of license key."""
        if obj.license_key:
            key = obj.license_key
            if len(key) > 30:
                return f"{key[:20]}...{key[-10:]}"
            return key
        return "-"

    @admin.display(description=_("Linked Equipment"))
    def linked_equipment(self, obj: License) -> str:
        """Display linked equipment."""
        if hasattr(obj, "kalmar32_license") and obj.kalmar32_license:
            return format_html(
                '<a href="/admin/core/kalmar32/{}/change/">Kalmar32: {}</a>',
                obj.kalmar32_license.id,
                obj.kalmar32_license.serial_number,
            )
        if hasattr(obj, "phasar01_license") and obj.phasar01_license:
            return format_html(
                '<a href="/admin/core/phasar01/{}/change/">Phasar01: {}</a>',
                obj.phasar01_license.id,
                obj.phasar01_license.serial_number,
            )
        return "Not linked"