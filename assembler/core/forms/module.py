"""Module defining ModuleForm for handling Module model forms.

This module contains the ModuleForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Module model.
"""

from __future__ import annotations

from typing import ClassVar

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget

from core.forms.base import BaseStyledForm
from core.models import Machine, Manufacturer, Module


class ModuleForm(BaseStyledForm):
    """Form for creating or updating a Module instance.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            A mapping of form field names to their placeholder text in Russian.

    """

    placeholders: ClassVar[dict[str, str]] = {
        "decimal": _("Децимальный номер"),
        "name": _("Название модуля"),
        "version": _("Версия"),
        "description": _("Описание"),
        "manufacturer": _("Производитель"),
        "scheme_file": "PDF файл чертежа",
        "step_file": "STEP файл модели",
    }

    select2_fields: ClassVar[dict[str, tuple]] = {
        "parent": (Module, ["name__icontains", "decimal__icontains"]),
        "manufacturer": (Manufacturer, ["name__icontains"]),
    }

    class Meta:
        """Metadata for ModuleForm."""

        model = Module
        fields = (
            "name",
            "decimal",
            "version",
            "machines",
            "parent",
            "manufacturer",
            "description",
            "module_status",
            "scheme_file",
            "step_file",
        )
        widgets: ClassVar[dict[str, object]] = {
            "machines": ModelSelect2MultipleWidget(
                model=Machine,
                search_fields=["name__icontains"],
            ),
        }

    def clean_parent(self) -> Module | None:
        """Validate the 'parent' field during form cleaning.

        This validation performs three main checks:
        1. Ensures that the parent module is not the module itself.
        2. Ensures that the parent module shares at least one machine with
           the current module.
        3. Prevents cyclic references in the module hierarchy.
        """
        parent = self.cleaned_data.get("parent")
        if parent and self.instance and parent.id == self.instance.id:
            error_msg = "Модуль не может быть родительским сам себе."
            raise ValidationError(error_msg)

        # Проверяем пересечение машин
        if parent and self.cleaned_data.get("machines"):
            parent_machines = set(parent.machines.all())
            current_machines = set(self.cleaned_data["machines"])
            if not parent_machines & current_machines:
                error_msg = (
                    "Родительский модуль должен быть связан хотя бы с одной "
                    "той же машиной, что и текущий модуль."
                )
                raise ValidationError(error_msg)

        ancestor = parent
        while ancestor:
            if ancestor.id == self.instance.id:
                error_msg = "Циклическая связь модулей недопустима."
                raise ValidationError(error_msg)
            ancestor = ancestor.parent
        return parent
