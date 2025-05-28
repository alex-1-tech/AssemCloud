"""Module defining BlueprintForm for handling Blueprint model forms.

This module contains the BlueprintForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Blueprint model.
"""

from typing import ClassVar

from core.forms.base import BaseStyledForm
from core.models import Blueprint, User


class BlueprintForm(BaseStyledForm):
    """Form for creating or updating a Blueprint instance.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            A mapping of form field names to their placeholder text in Russian.

    """

    placeholders: ClassVar[dict[str, str]] = {
        "weight": "Масса в кг",
        "scale": "Например: 1:10",
        "version": "v1.0",
        "naming_scheme": "Схема наименования",
        "scheme_file": "PDF файл чертежа",
        "step_file": "STEP файл модели",
    }

    container = (User, [
            "first_name__icontains",
            "last_name__icontains",
            "email__icontains",
        ])
    select2_fields: ClassVar[dict[str, tuple]] = {
        "developer": container,
        "validator": container,
        "lead_designer": container,
        "chief_designer": container,
        "approver": container,
    }

    class Meta:
        """Metadata for BlueprintForm."""

        model = Blueprint
        fields = (
            "weight",
            "scale",
            "version",
            "naming_scheme",
            "developer",
            "validator",
            "lead_designer",
            "chief_designer",
            "approver",
            "scheme_file",
            "step_file",
        )
