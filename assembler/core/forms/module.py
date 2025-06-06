"""Module defining ModuleForm for handling Module model forms.

This module contains the ModuleForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Module model.
"""

from __future__ import annotations

from typing import ClassVar

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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
        "machine": (Machine, ["name__icontains"]),
        "parent": (Module, ["name__icontains", "serial__icontains"]),
        "manufacturer": (Manufacturer, ["name__icontains"]),
    }

    class Meta:
        """Metadata for ModuleForm."""

        model = Module
        fields = (
            "name",
            "decimal",
            "version",
            "machine",
            "parent",
            "manufacturer",
            "description",
            "module_status",
            "scheme_file",
            "step_file",
        )


    def clean_parent(self) -> Module | None:
        """Validate the 'parent' field during form cleaning.

        This validation performs two main checks:
        1. Ensures that the parent module is not the module itself
            (a module cannot be its own parent).
         2. Ensures that the parent module belongs to the same machine
            as the current module. This prevents assigning a parent
            from a different machine, which would break logical consistency.
        3. Prevents cyclic references in the module hierarchy
            to avoid infinite loops in nested modules.
        """
        parent = self.cleaned_data.get("parent")
        if parent and self.instance and parent.id == self.instance.id:
            error_msg = "Модуль не может быть родительским сам себе."
            raise ValidationError(error_msg)

        if parent and parent.machine.id != self.cleaned_data.get("machine").id:
            error_msg = "Родительский модуль должен принадлежть той же машине."
            raise ValidationError(error_msg)

        ancestor = parent
        while ancestor:
            if ancestor.id == self.instance.id:
                error_msg = "Циклическая связь модулей недопустима."
                raise ValidationError(error_msg)
            ancestor = ancestor.parent
        return parent
