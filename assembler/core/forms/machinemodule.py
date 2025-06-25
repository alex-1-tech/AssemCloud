"""Module defining MachineModuleForm for handling MachineModule model forms.

This module contains the MachineModuleForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the MachineModule model.
"""

from __future__ import annotations

from typing import ClassVar

from django.core.exceptions import ValidationError

from core.forms.base import BaseStyledForm
from core.models import Machine, MachineModule, Module


class MachineModuleForm(BaseStyledForm):
    """Form for creating or updating a MachineModule instance."""

    placeholders: ClassVar[dict[str, str]] = {
        "module": "Модуль",
        "machine": "Машина",
        "parent_module": "Родительский модуль",
        "quantity": "Количество",
    }

    select2_fields: ClassVar[dict[str, tuple]] = {
        "module": (Module, ["name__icontains", "decimal__icontains"]),
        "machine": (Machine, ["name__icontains"]),
        "parent_module": (Module, ["name__icontains"]),
    }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Init MachineModuleForm method."""
        super().__init__(*args, **kwargs)
        self.fields["module"].queryset = Module.objects.all()
        self.fields["machine"].queryset = Machine.objects.all()
        self.fields["parent_module"].queryset = Module.objects.all()

    class Meta:
        """Metadata for MachineModuleForm."""

        model = MachineModule
        fields = ("machine", "parent_module", "module", "quantity")

    def clean_parent(self) -> MachineModule | None:
        """Validate the 'parent' field during form cleaning.

        This validation performs three main checks:
        1. Ensures that the parent module is not the same as the current module.
        2. Ensures that the parent module is not a child of the current module.
        3. Ensures that the parent module is not a descendant of the current module.
        """
        parent = self.cleaned_data.get("parent_module")
        if parent and parent == self.cleaned_data.get("module"):
            msg = "Родительский модуль не может быть тем же, что и модуль."
            raise ValidationError(msg)
        ancetor = parent
        while ancetor:
            if ancetor == self.cleaned_data.get("module"):
                msg = "Циклическая связь модулей недопустима."
                raise ValidationError(msg)
            ancetor = ancetor.parent_module
        return parent
