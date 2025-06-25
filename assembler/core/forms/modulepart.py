"""Module defining ModulePartForm for handling ModulePart model forms.

This module contains the ModulePartForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the ModulePart model.
"""

from typing import ClassVar

from core.forms.base import BaseStyledForm
from core.models import Module, ModulePart, Part


class ModulePartForm(BaseStyledForm):
    """Form for creating or updating a ModulePart instance."""

    placeholders: ClassVar[dict[str, str]] = {
        "module": "Модуль",
        "part": "Изделие",
        "quantity": "Количество",
    }

    select2_fields: ClassVar[dict[str, tuple]] = {
        "module": (Module, ["name__icontains", "decimal__icontains"]),
        "part": (Part, ["name__icontains"]),
    }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Init ModulePartForm method."""
        super().__init__(*args, **kwargs)
        self.fields["module"].queryset = Module.objects.all()
        self.fields["part"].queryset = Part.objects.all()

    class Meta:
        """Metadata for ModulePartForm."""

        model = ModulePart
        fields = ("module", "part", "quantity")
