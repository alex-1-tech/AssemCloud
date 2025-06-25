"""Admin configuration for core app models.

Includes admin interfaces and inline configurations for User, Role,
Client, Manufacturer, Machine, Module, Part, and change logging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.models import (
    ChangesLog,
    Client,
    Machine,
    MachineClient,
    MachineModule,
    Manufacturer,
    Module,
    ModulePart,
    Part,
    Role,
    User,
    UserRole,
)

if TYPE_CHECKING:
    from django.http import HttpRequest


# =================== INLINE ===================


class ModulePartInline(admin.TabularInline):
    """Inline display of module parts directly inside the module form."""

    model = ModulePart
    extra = 0
    autocomplete_fields = ("part",)
    classes: ClassVar[list[str]] = ["collapse"]  # collapse the block by default


class MachineModuleInline(admin.TabularInline):
    """Inline display of machine modules directly inside the machine form."""

    model = MachineModule
    extra = 0
    autocomplete_fields = ("module",)
    classes: ClassVar[list[str]] = ["collapse"]


# =================== USERS ===================


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin configuration for the User model."""

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "date_joined",
        "is_email_verified",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff")
    readonly_fields = ("date_joined", "last_login")
    fieldsets = (
        (
            _("Basic Information"),
            {"fields": ("email", "first_name", "last_name", "phone")},
        ),
        (
            _("Access Rights"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("System Information"), {"fields": ("date_joined", "last_login")}),
    )


# =================== ROLES ===================


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin configuration for the Role model."""

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin configuration for the UserRole model."""

    list_display = ("user", "role")
    search_fields = ("user__email", "role__name")
    autocomplete_fields = ("user", "role")


# =================== CLIENTS ===================


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin configuration for the Client model."""

    list_display = ("name", "country", "phone")
    search_fields = ("name__icontains", "country")
    list_filter = ("country",)


# =================== MANUFACTURERS ===================


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    """Admin configuration for the Manufacturer model."""

    list_display = ("name", "country", "language", "phone")
    search_fields = ("name__icontains", "country")
    list_filter = ("country",)


# =================== MACHINE ===================


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    """Admin configuration for the Machine model."""

    list_display = ("name", "version")
    search_fields = ("name__icontains",)


@admin.register(MachineClient)
class MachineClientAdmin(admin.ModelAdmin):
    """Admin configuration for the MachineClient model."""

    list_display = ("machine", "get_clients", "created_at")
    search_fields = ("machine__name", "client__name")
    list_filter = ("machine", "client")
    autocomplete_fields = ("machine", "client")

    def get_clients(self, obj: MachineClient) -> str:
        """Return a comma-separated list of clients linked to the machine."""
        return ", ".join(client.name for client in obj.clients.all())

    get_clients.short_description = _("Clients")


# =================== MODULE ===================


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin configuration for the Module model, highlighting new fields and structure.

    Shows key technical and manufacturing fields, including status, parent, manufacturer
    and blueprint files (PDF, STEP).
    Supports hierarchy and filtering by status and machine.
    """

    list_display = (
        "name",
        "version",
        "manufacturer",
        "module_status",
        "scheme_file",
        "step_file",
    )
    search_fields = (
        "name__icontains",
        "manufacturer__name__icontains",
        "decimal",
        "version",
    )
    list_filter = ("module_status", "manufacturer")
    autocomplete_fields = ("manufacturer",)
    inlines: ClassVar[list[str]] = [ModulePartInline]


# =================== PART ===================


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    """Admin configuration for the Part model."""

    list_display = ("name", "manufacturer")
    search_fields = ("name__icontains", "manufacturer")
    autocomplete_fields = ("manufacturer",)


@admin.register(ModulePart)
class ModulePartAdmin(admin.ModelAdmin):
    """Admin configuration for the ModulePart model."""

    list_display = ("module", "part", "quantity")
    search_fields = ("module__name", "part__name")
    list_filter = ("module", "part")
    autocomplete_fields = ("module", "part")


# =================== CHANGE LOG ===================


@admin.register(ChangesLog)
class ChangesLogAdmin(admin.ModelAdmin):
    """Admin configuration for the ChangesLog model."""

    list_display = (
        "log_id",
        "table_name",
        "linked_id_record",
        "column_name",
        "old_value",
        "new_value",
        "linked_user",
        "changed_on",
    )
    search_fields = ("table_name", "changed_by__email", "changed_on")
    list_filter = ("table_name", "changed_by", "changed_on")
    readonly_fields = (
        "table_name",
        "record_id",
        "column_name",
        "old_value",
        "new_value",
        "changed_by",
        "changed_on",
    )
    ordering = ("-changed_on",)
    date_hierarchy = "changed_on"
    list_per_page = 25

    def linked_user(self, obj: ChangesLog) -> str | None:
        """Return a link to the user who made the change."""
        if obj.changed_by:
            return format_html(
                '<a href="/admin/core/user/{}/change/">{}</a>',
                obj.changed_by.pk,
                obj.changed_by.email,
            )
        return "-"

    linked_user.short_description = _("User")

    def linked_id_record(self, obj: ChangesLog) -> str:
        """Return a link to the changed record."""
        if obj.record_id:
            return format_html(
                '<a href="/admin/core/{}/{}/change/">{}</a>',
                obj.table_name.lower(),
                obj.record_id,
                obj.record_id,
            )
        return "-"

    linked_id_record.short_description = _("Record ID")

    def has_add_permission(self, request: HttpRequest) -> bool:  # noqa: ARG002
        """Disable manual addition of change logs."""
        return False

    def has_change_permission(
        self,
        request: HttpRequest,  # noqa: ARG002
        obj: ChangesLog | None = None,  # noqa: ARG002
    ) -> bool:
        """Disable editing of change logs."""
        return False
