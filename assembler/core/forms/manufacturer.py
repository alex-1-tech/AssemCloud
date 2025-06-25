"""Module defining ManufacturerForm for handling Manufacturer model forms.

This module contains the ManufacturerForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Manufacturer model.
"""

from typing import ClassVar

from core.forms.base import BaseStyledForm
from core.models import Manufacturer


class ManufacturerForm(BaseStyledForm):
    """Form for creating or updating a Manufacturer instance.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            A mapping of form field names to their placeholder text or example values.

    """

    placeholders: ClassVar[dict[str, str]] = {
        "name": "Название",
        "country": "Страна",
        "language": "ru",
        "phone": "+79991234567",
    }

    class Meta:
        """Metadata for ManufacturerForm."""

        model = Manufacturer
        fields = ("name", "country", "language", "phone")
