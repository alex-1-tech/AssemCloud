"""Module defining BaseStyledForm as a base class for styled model forms.

This module contains the BaseStyledForm class, which extends Django's ModelForm,
adding placeholder support and default CSS classes to form fields.
"""

from typing import ClassVar

from django import forms
from django_select2.forms import ModelSelect2Widget


class BaseStyledForm(forms.ModelForm):
    """Base form class that adds placeholders and CSS classes to form fields.

    Attributes:
        placeholders (ClassVar[dict[str, str]]):
            Mapping of field names to placeholder text.
        select2_fields (ClassVar[dict[str, tuple]]):
            Mapping of field names to a tuple (model, search_fields) for Select2 widgets

    """

    placeholders: ClassVar[dict[str, str]] = {}
    select2_fields: ClassVar[dict[str, tuple]] = {}

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Init form: placeholders, CSS, select2, queryset."""
        super().__init__(*args, **kwargs)

        for name, text in self.placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs["placeholder"] = text

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        for name, (model, search_fields) in self.select2_fields.items():
            if name in self.fields:
                self.fields[name].widget = ModelSelect2Widget(
                    model=model,
                    search_fields=search_fields,
                    attrs={
                        "class": "django-select2 form-select",
                        "style": "width: 100%;",
                    },
                )

        for field_name, (model_cls, _) in self.select2_fields.items():
            if field_name in self.fields and hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value:
                    qs = model_cls.objects.filter(pk=value.pk) | model_cls.objects.all()
                    self.fields[field_name].queryset = qs.distinct()
