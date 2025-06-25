"""Module defining ModuleForm for handling Module model forms.

This module contains the ModuleForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Module model.
"""

from __future__ import annotations

from typing import ClassVar

from django.utils.translation import gettext_lazy as _

from core.forms.base import BaseStyledForm
from core.models import Manufacturer, Module


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
        "manufacturer": (Manufacturer, ["name__icontains"]),
    }

    class Meta:
        """Metadata for ModuleForm."""

        model = Module
        fields = (
            "name",
            "decimal",
            "version",
            "manufacturer",
            "description",
            "module_status",
            "scheme_file",
            "step_file",
        )
