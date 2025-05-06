from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.models import (
    User, Role, UserRole, Client, Manufacturer,
    Blueprint, Machine, MachineClient, Module, Part, PartManufacture, ModulePart,
    ChangesLog,
)


# =================== INLINE ===================

class ModulePartInline(admin.TabularInline):
    """
    Отображение составных частей модуля прямо внутри формы модуля
    """
    model = ModulePart
    extra = 0
    autocomplete_fields = ('part',)
    classes = ['collapse'] # свернуть блок по умолчанию


# =================== USERS ===================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Системная информация'), {
            'fields': ('date_joined', 'last_login')
        }),
    )


# =================== ROLES ===================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role',)
    search_fields = ('user__email', 'role__name',)
    autocomplete_fields = ('user', 'role',)


# =================== CLIENTS ===================

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'phone',)
    search_fields = ('name__icontains', 'country')
    list_filter = ('country',)


# =================== MANUFACTURERS ===================

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'language', 'phone')
    search_fields = ('name__icontains', 'country')
    list_filter = ('country',)


# =================== BLUEPRINT ===================

@admin.register(Blueprint)
class BlueprintAdmin(admin.ModelAdmin):
    list_display = ('naming_scheme', 'version', 'manufacturer', 'developer')
    search_fields = ('naming_scheme__icontains', 'manufacturer__name', 'developer__email')
    list_filter = ('developer',)
    autocomplete_fields = ('manufacturer', 'developer')


# =================== MACHINE ===================

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'version')
    search_fields = ('name__icontains',)


@admin.register(MachineClient)
class MachineClientAdmin(admin.ModelAdmin):
    list_display = ('machine', 'get_clients', 'created_at')
    search_fields = ('machine__name', 'client__name')
    list_filter = ('machine', 'client')
    autocomplete_fields = ('machine', 'client')

    # Кастомное поле для отображения клиентов машины
    def get_clients(self, obj):
        return ", ".join([client.name for client in obj.clients.all()])
    get_clients.short_description = _('Клиенты')


# =================== MODULE ===================

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'machine', 'parent', 'module_status')
    search_fields = ('name__icontains', 'machine__name__icontains', 'parent__name__icontains')
    list_filter = ('machine', 'module_status')
    autocomplete_fields = ('machine', 'parent')
    inlines = [ModulePartInline]


# =================== PART ===================

@admin.register(PartManufacture)
class PartManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id', 'manufacturer')
    search_fields = ('id',)
    list_filter = ('manufacturer',)
    autocomplete_fields = ('manufacturer',)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_manufacture')
    search_fields = ('name__icontains',)
    autocomplete_fields = ('part_manufacture',)


@admin.register(ModulePart)
class ModulePartAdmin(admin.ModelAdmin):
    list_display = ('module', 'part', 'quantity')
    search_fields = ('module__name', 'part__name')
    list_filter = ('module', 'part')
    autocomplete_fields = ('module', 'part')


# =================== CHANGE LOG ===================

@admin.register(ChangesLog)
class ChangesLogAdmin(admin.ModelAdmin):
    list_display = (
        'log_id', 'table_name', 'record_id', 'column_name',
        'old_value', 'new_value', 'linked_user', 'changed_on',
    )
    search_fields = ('table_name', 'changed_by__email', 'changed_on')
    list_filter = ('table_name', 'changed_by', 'changed_on')
    readonly_fields = (
        'table_name', 'record_id', 'column_name',
        'old_value', 'new_value', 'changed_by', 'changed_on',
    )
    ordering = ('-changed_on',)
    date_hierarchy = 'changed_on'
    list_per_page = 25

    # Ссылка на пользователя, кто внёс изменение
    def linked_user(self, obj):
        if obj.changed_by:
            return format_html(
                '<a href="/admin/core/user/{}/change/">{}</a>',
                obj.changed_by.pk,
                obj.changed_by.email
            )
        return "-"
    linked_user.short_description = _("Пользователь")

    # Запрет добавления логов вручную
    def has_add_permission(self, request):
        return False

    # Запрет редактирования логов
    def has_change_permission(self, request, obj=None):
        return False
