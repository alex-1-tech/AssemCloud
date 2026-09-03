from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING, Any, ClassVar

from django import forms
from django.contrib import admin
from django.forms.widgets import Textarea
from django.urls import path
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _

from core.models import Equipment, EquipmentType, Model, Scheme
from core.views import get_schemes_for_model

if TYPE_CHECKING:
    from django.db import models
    from django.forms import Widgets


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    """Admin configuration for EquipmentType."""

    list_display = ("name", "title", "description", "installer_path", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "title", "description")
    ordering = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "title", "description", "installer_path", "is_active"),
            },
        ),
    )


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    """Admin configuration for managing hardware model variants."""

    list_display = ("equipment_type", "version", "type_rail", "is_active")
    list_filter = ("equipment_type", "type_rail", "is_active")
    search_fields = ("equipment_type__name", "version")
    ordering = ("equipment_type__name", "version")
    fieldsets = (
        (
            _("Model Info"),
            {
                "fields": ("equipment_type", "version", "type_rail", "is_active"),
            },
        ),
    )


class PrettyJSONWidget(Textarea):
    """Textarea widget that automatically indents and formats JSON content."""

    def format_value(self, value: Any) -> str | None:
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return value
        return json.dumps(value, indent=4, ensure_ascii=False)


class SchemeAdminForm(forms.ModelForm):
    """Form providing formatted JSON editing for Scheme model."""

    class Meta:
        model = Scheme
        fields = "__all__"
        widgets: ClassVar[dict[type[models.Field], dict[str, Widgets]]] = {
            "fields_description": PrettyJSONWidget(
                attrs={
                    "rows": 30,
                    "cols": 100,
                    "style": "font-family: monospace; font-size: 13px; line-height: 1.4; tab-size: 4;",
                },
            ),
        }


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    """Admin configuration for managing JSON field schemes."""

    form = SchemeAdminForm
    list_display = ("equipment_type", "version", "is_latest", "get_scheme_fields_summary")
    readonly_fields = ("get_scheme_fields_summary",)
    list_filter = ("equipment_type", "is_latest")
    search_fields = ("equipment_type__name",)
    ordering = ("equipment_type__name", "-version")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "equipment_type",
                    "version",
                    "is_latest",
                    "get_scheme_fields_summary",
                    "fields_description",
                ),
            },
        ),
    )

    @admin.display(description=_("Declared Fields"))
    def get_scheme_fields_summary(self, obj: Scheme) -> str:
        """Parse nested sections from fields_description and format fields grouped by section titles."""
        if not obj.fields_description or not isinstance(obj.fields_description, dict):
            return "-"

        sections = obj.fields_description.get("sections")
        if not isinstance(sections, list):
            return "-"

        section_blocks: list[str] = []
        for section in sections:
            if not isinstance(section, dict):
                continue

            section_title = section.get("title") or section.get("key") or _("Section")
            fields = section.get("fields")

            if not isinstance(fields, list):
                continue

            field_lines: list[str] = []
            for field in fields:
                if not isinstance(field, dict):
                    continue

                name = field.get("name", "")
                label = field.get("label", "")

                if name and label:
                    field_lines.append(format_html("&nbsp;&nbsp;• <b>{}</b> ({})", name, label))
                elif name:
                    field_lines.append(format_html("&nbsp;&nbsp;• <b>{}</b>", name))

            if field_lines:
                joined_fields = format_html_join("<br>", "{}", ((line,) for line in field_lines))
                block = format_html("<b>{}</b>:<br>{}", section_title, joined_fields)
                section_blocks.append(block)

        if not section_blocks:
            return "-"

        return format_html_join("<br><br>", "{}", ((block,) for block in section_blocks))


class EquipmentAdminForm(forms.ModelForm):
    """Form that dynamically generates form fields for `other_data` JSON based on selected Scheme."""

    class Meta:
        model = Equipment
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        model_id = None
        if self.data.get("model"):
            model_id = self.data.get("model")
        elif self.instance and self.instance.pk and self.instance.model_id:
            model_id = self.instance.model_id

        if model_id:
            self.fields["scheme"].queryset = Scheme.objects.for_model(model_id=model_id)
        else:
            self.fields["scheme"].queryset = Scheme.objects.none()

        scheme_obj = None
        if self.data.get("scheme"):
            with contextlib.suppress(Scheme.DoesNotExist):
                scheme_obj = Scheme.objects.get(pk=self.data.get("scheme"))
        elif self.instance and self.instance.pk and self.instance.scheme:
            scheme_obj = self.instance.scheme

        if scheme_obj and isinstance(scheme_obj.fields_description, dict):
            sections = scheme_obj.fields_description.get("sections", [])
            existing_data = self.instance.other_data or {} if self.instance else {}

            for section in sections:
                if not isinstance(section, dict):
                    continue

                for field_def in section.get("fields", []):
                    if not isinstance(field_def, dict):
                        continue

                    field_name = field_def.get("name")
                    if not field_name:
                        continue

                    field_key = f"json_field_{field_name}"
                    field_type = field_def.get("type", "string")

                    label = field_def.get("label") or field_name
                    required = field_def.get("required", False)
                    initial_val = existing_data.get(field_name, field_def.get("default"))

                    if field_type == "boolean":
                        self.fields[field_key] = forms.BooleanField(
                            label=label,
                            required=required,
                            initial=initial_val,
                        )
                    elif field_type == "text":
                        self.fields[field_key] = forms.CharField(
                            label=label,
                            required=required,
                            initial=initial_val,
                            widget=forms.Textarea(attrs={"rows": 3}),
                        )
                    elif field_type in ("integer", "int"):
                        self.fields[field_key] = forms.IntegerField(
                            label=label,
                            required=required,
                            initial=initial_val,
                        )
                    else:
                        max_len = field_def.get("max_length", 255)
                        self.fields[field_key] = forms.CharField(
                            label=label,
                            required=required,
                            max_length=max_len,
                            initial=initial_val,
                        )

    def save(self, commit: bool = True) -> Equipment:
        """Collect dynamic `json_field_*` inputs and serialize them into `other_data` JSONField."""
        instance = super().save(commit=False)
        other_data = dict(instance.other_data or {})

        for field_name, value in self.cleaned_data.items():
            if field_name.startswith("json_field_"):
                key = field_name.replace("json_field_", "", 1)
                other_data[key] = value

        instance.other_data = other_data
        if commit:
            instance.save()
            self.save_m2m()
        return instance


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Admin configuration for Equipment with model-dependent scheme choice and interactive JSON fields."""

    form = EquipmentAdminForm
    list_display = (
        "serial_number",
        "get_model_display",
        "scheme",
        "shipment_date",
        "invoice",
        "license",
    )
    list_filter = (
        "model__equipment_type",
        "model__type_rail",
        "scheme__version",
        "shipment_date",
    )
    search_fields = (
        "serial_number",
        "invoice",
        "packet_list",
        "license__license_key",
    )
    date_hierarchy = "shipment_date"
    ordering = ("-shipment_date",)

    fieldsets = (
        (
            _("Registration Data"),
            {
                "fields": (
                    "serial_number",
                    "model",
                    "scheme",
                    "shipment_date",
                    "invoice",
                    "packet_list",
                    "license",
                ),
            },
        ),
        (
            None,
            {
                "fields": ("other_data",),
            },
        ),
    )

    class Media:
        js = ("admin/js/equipment_scheme_filter.js",)
        css = {"all": ("admin/css/equipment_scheme_filter.css",)}

    @admin.display(description=_("Model Variant"), ordering="model__equipment_type__name")
    def get_model_display(self, obj: Equipment) -> str:
        return str(obj.model)

    def get_urls(self):
        custom_urls = [
            path(
                "get-schemes/",
                self.admin_site.admin_view(get_schemes_for_model),
                name="core_equipment_get_schemes",
            ),
        ]
        return custom_urls + super().get_urls()
