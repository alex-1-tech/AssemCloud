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
        "machine": "Машина",
        "module_link": "Модуль (справочник)",
        "parent_module_link": "Родительский модуль (справочник)",
        "module": "Узел иерархии (дочерний)",
        "parent_module": "Узел иерархии (родительский)",
        "quantity": "Количество",
    }

    select2_fields: ClassVar[dict[str, tuple]] = {
        "machine": (Machine, ["name__icontains"]),
        "module_link": (Module, ["name__icontains", "decimal__icontains"]),
        "parent_module_link": (Module, ["name__icontains", "decimal__icontains"]),
        "parent_module": (MachineModule, ["module_link__name__icontains"]),
    }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Init MachineModuleForm method."""
        super().__init__(*args, **kwargs)
        self.fields["module_link"].queryset = Module.objects.all()
        self.fields["parent_module_link"].queryset = Module.objects.all()
        self.fields["machine"].queryset = Machine.objects.all()
        self.fields["module"].queryset = MachineModule.objects.all()
        self.fields["parent_module"].queryset = MachineModule.objects.all()

        if self.instance and self.instance.pk:
            self.fields["module"].queryset = \
                self.fields["module"].queryset.exclude(pk=self.instance.pk)
            self.fields["parent_module"].queryset = \
                self.fields["parent_module"].queryset.exclude(pk=self.instance.pk)


    class Meta:
        """Metadata for MachineModuleForm."""

        model = MachineModule
        fields = (
            "machine",
            "module_link",
            "parent_module_link",
            "parent_module",
            "module",
            "quantity",
        )

    def clean_parent(self) -> MachineModule | None:
        """Validate the 'parent' field during form cleaning.

        This validation performs three main checks:
        1. Ensures that the parent module is not the same as the current module.
        2. Ensures that the parent module is not a child of the current module.
        3. Ensures that the parent module is not a descendant of the current module.
        """
        parent = self.cleaned_data.get("parent_module")
        if not parent:
            return None

        if self.instance.pk and parent.pk == self.instance.pk:
            msg = "Родительский узел не может быть тем же, что и текущий."
            raise ValidationError(msg)

        ancestor = parent
        while ancestor is not None:
            if self.instance.pk and ancestor.pk == self.instance.pk:
                msg = "Циклическая связь узлов недопустима."
                raise ValidationError(msg)
            ancestor = ancestor.parent_module
        return parent
