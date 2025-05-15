"""Module defining MachineForm for handling Machine model forms.

This module contains the MachineForm class, which extends BaseStyledForm,
providing form fields, placeholder configurations,
and custom widget attributes for the Machine model.
"""

from typing import ClassVar

from core.forms.base import BaseStyledForm
from core.models import Machine


class MachineForm(BaseStyledForm):
    """Form for creating or updating a Machine instance.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            A mapping of form field names to their placeholder text in Russian.

    """

    placeholders: ClassVar[dict[str, str]] = {
        "name": "Название машины",
        "version": "Версия машины",
    }

    class Meta:
        """Metadata for MachineForm."""

        model = Machine
        fields = ("name", "version", "clients")

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize the form and customize the 'clients' field widget."""
        super().__init__(*args, **kwargs)
        self.fields["clients"].widget.attrs.update(
            {"class": "form-select", "multiple": "multiple"},
        )
