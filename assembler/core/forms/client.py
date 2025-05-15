"""Module defining ClientForm for handling Client model forms.

This module contains the ClientForm class, which extends BaseStyledForm,
providing form fields and placeholder configurations for the Client model.
"""

from typing import ClassVar

from core.forms.base import BaseStyledForm
from core.models import Client


class ClientForm(BaseStyledForm):
    """Form for creating or updating a Client instance.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            A mapping of form field names to their placeholder text in Russian.

    """

    placeholders: ClassVar[dict[str, str]] = {
        "name": "Название клиента",
        "country": "Страна",
        "phone": "+79991234567",
    }

    class Meta:
        """Metadata for ClientForm."""

        model = Client
        fields = ("name", "country", "phone")
