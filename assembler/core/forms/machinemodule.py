"""Module defining MachineModuleForm for handling MachineModule model forms.

This module contains the MachineModuleForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the MachineModule model.
"""

from __future__ import annotations

import contextlib
from typing import ClassVar

from django.core.exceptions import ValidationError

from core.forms.base import BaseStyledForm
from core.models import Machine, MachineModule, Module


class MachineModuleForm(BaseStyledForm):
    """Form for creating or updating a MachineModule instance."""

    placeholders: ClassVar[dict[str, str]] = {
        "machine": "Машина",
        "module": "Модуль",
        "parent": "Родительский модуль",
        "quantity": "Количество",
    }

    select2_fields: ClassVar[dict[str, tuple]] = {
        "machine": (Machine, ["name__icontains"]),
        "module": (Module, ["name__icontains", "decimal__icontains"]),
        "parent": (Module, ["name__icontains", "decimal__icontains"]),
    }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Init MachineModuleForm method."""
        initial = kwargs.get("initial") or {}

        super().__init__(*args, **kwargs)
        self.fields["module"].queryset = Module.objects.all()
        self.fields["parent"].queryset = Module.objects.all()
        self.fields["machine"].queryset = Machine.objects.all()

        mode = None
        if "mode" in initial:
            mode = initial["mode"]
        if mode == "machine":
            self.fields.pop("parent", None)
        elif mode == "parentmodule":
            self.fields.pop("machine", None)

    class Meta:
        """Metadata for MachineModuleForm."""

        model = MachineModule
        fields = (
            "machine",
            "parent",
            "module",
            "quantity",
        )

    def clean(self) -> object:
        """Validate the 'module' field during form cleaning.

        This validation performs three main checks:
        1. Ensures that the parent module is not the same as the current module.
        2. Ensures that the parent module is not a child of the current module.
        3. Ensures that the parent module is not a descendant of the current module.
        """
        cleaned_data = super().clean()
        parent = self.cleaned_data.get("parent")
        module = self.cleaned_data.get("module")
        if not parent:
            return cleaned_data
        if not module:
            msg = "Модуль обязателен."
            raise ValidationError(msg)
        if not parent or not module:
            msg = "Модуль обязателен."
            raise ValidationError(msg)
        if parent.pk == module.pk:
            msg = "Родительский узел не может быть тем же, что и текущий."
            raise ValidationError(msg)

        visited = set()
        stack = [parent]

        while stack:
            current_module = stack.pop()
            if current_module.pk in visited:
                continue
            visited.add(current_module.pk)

            # все MachineModule, где module == current_module
            q = MachineModule.objects.filter(module=current_module)
            for mm in q:
                # при редактировании пропускаем себя
                if self.instance.pk and mm.pk == self.instance.pk:
                    continue
                next_parent = mm.parent
                if not next_parent:
                    continue
                if next_parent.pk == module.pk:
                    msg = "Циклическая связь узлов недопустима."
                    raise ValidationError(msg)
                stack.append(next_parent)
        return cleaned_data
