"""Module defining MachineForm for handling Machine model forms.

This module contains the MachineForm class, which extends BaseStyledForm,
providing form fields, placeholder configurations,
and custom widget attributes for the Machine model.
"""

from typing import ClassVar

from django_select2.forms import ModelSelect2MultipleWidget

from core.forms.base import BaseStyledForm
from core.models import Client, Machine


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
        fields = ("name", "version", "status", "clients")
        widgets: ClassVar[dict[str, object]] = {
            "clients": ModelSelect2MultipleWidget(
                model=Client,
                search_fields=["name__icontains"],
            ),
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize the form with styled fields and placeholder support."""
        super().__init__(*args, **kwargs)

        # Select2 already applies its own styling, so avoid overriding it
        if "clients" in self.fields:
            self.fields["clients"].widget.attrs.pop("class", None)
            self.fields["clients"].widget.attrs.update(
                {
                    "style": "width: 100%; min-height: 40px;",
                }
            )
