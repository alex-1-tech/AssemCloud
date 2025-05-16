"""Module defining PartForm for handling Part model forms.

This module contains the PartForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Part model.
"""
from typing import ClassVar

from django import forms

from core.forms.base import BaseStyledForm
from core.models import Part


class PartForm(BaseStyledForm):
    """Form for creating or updating a Part instance.

    Attributes:
        placeholders (ClassVar[Dict[str, str]]):
            A mapping of form field names to their placeholder text in Russian.

    """

    placeholders: ClassVar[dict[str, str]] = {
        "name": "Название",
        "manufacturer": "Производитель",
        "description": "Описание",
        "material": "Материал",
        "manufacture_date": "Дата производства",
    }

    class Meta:
        """Metadata for PartForm."""

        model = Part
        fields = ("name", "manufacturer", "description", "material", "manufacture_date")
        widgets: ClassVar[dict[str, object]] = {
            "manufacture_date": forms.DateInput(attrs={"type": "date"}),
        }
