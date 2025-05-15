"""Module defining ModulePartForm for handling ModulePart model forms.

This module contains the ModulePartForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the ModulePart model.
"""

from typing import ClassVar

from core.forms.base import BaseStyledForm
from core.models import ModulePart


class ModulePartForm(BaseStyledForm):
    """Form for creating or updating a ModulePart instance.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            A mapping of form field names to their placeholder text in Russian.

    """

    placeholders: ClassVar[dict[str, str]] = {
        "module": "Модуль",
        "part": "Деталь",
        "quantity": "Количество",
    }

    class Meta:
        """Metadata for ModulePartForm."""

        model = ModulePart
        fields = ("module", "part", "quantity")
