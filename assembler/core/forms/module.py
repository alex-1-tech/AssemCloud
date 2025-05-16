"""Module defining ModuleForm for handling Module model forms.

This module contains the ModuleForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Module model.
"""

from typing import ClassVar

from django.core.exceptions import ValidationError

from core.forms.base import BaseStyledForm
from core.models import Module


class ModuleForm(BaseStyledForm):
    """Form for creating or updating a Module instance.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            A mapping of form field names to their placeholder text in Russian.

    """

    placeholders: ClassVar[dict[str, str]] = {
        "part_number": "Артикул",
        "serial": "Серийный номер",
        "name": "Название модуля",
        "version": "Версия",
        "description": "Описание",
        "manufacturer": "Производитель",
    }

    class Meta:
        """Metadata for ModuleForm."""

        model = Module
        fields = (
            "machine",
            "blueprint",
            "part_number",
            "serial",
            "name",
            "parent",
            "manufacturer",
            "version",
            "description",
            "module_status",
        )

    def clean_parent(self) -> object:
        """Validate the 'parent' field during form cleaning.

        This validation performs two main checks:
        1. Ensures that the parent module is not the module itself
            (a module cannot be its own parent).
        2. Prevents cyclic references in the module hierarchy
            to avoid infinite loops in nested modules.
        """
        parent = self.cleaned_data.get("parent")
        if parent and self.instance and parent.id == self.instance.id:
            error_msg = "Модуль не может быть родительским сам себе."
            raise ValidationError(error_msg)

        ancestor = parent
        while ancestor:
            if ancestor.id == self.instance.id:
                error_msg = "Циклическая связь модулей недопустима."
                raise ValidationError(error_msg)
            ancestor = ancestor.parent
        return parent
