"""Module defining BaseStyledForm as a base class for styled model forms.

This module contains the BaseStyledForm class, which extends Django's ModelForm,
adding placeholder support and default CSS classes to form fields.
"""

from typing import ClassVar

from django import forms


class BaseStyledForm(forms.ModelForm):
    """Base form class that adds placeholders and CSS classes to form fields.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            A mapping of form field names to their placeholder text.

    """

    placeholders: ClassVar[dict[str, str]] = {}

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize the form, adding placeholders and default CSS classes."""
        super().__init__(*args, **kwargs)

        for name, text in self.placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs["placeholder"] = text

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
