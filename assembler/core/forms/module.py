"""Module defining ModuleForm for handling Module model forms.

This module contains the ModuleForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Module model.
"""

from typing import ClassVar

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
