"""BaseStyledForm: base class for styled model forms with placeholders."""

from __future__ import annotations

from typing import ClassVar

from django import forms
from django_select2.forms import ModelSelect2Widget


class BaseStyledForm(forms.ModelForm):
    """Base form class that adds placeholders and CSS classes to form fields."""

    placeholders: ClassVar[dict[str, str]] = {}
    select2_fields: ClassVar[dict[str, tuple[object, object]]] = {}

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize form and set placeholders, CSS, Select2 widgets, and querysets."""
        super().__init__(*args, **kwargs)

        self._set_placeholders()
        self._set_css_classes()
        self._set_select2_widgets()
        self._set_select2_querysets()

    def _set_placeholders(self) -> None:
        """Set placeholder attributes for form fields."""
        for name, text in self.placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs["placeholder"] = text

    def _set_css_classes(self) -> None:
        """Set default CSS classes for form fields."""
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def _set_select2_widgets(self) -> None:
        """Set Select2 widgets for specified fields."""
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

    def _set_select2_querysets(self) -> None:
        """Set queryset for Select2 fields based on instance value."""
        for field_name, (model_cls, _) in self.select2_fields.items():
            if field_name in self.fields and hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value:
                    self.fields[field_name].queryset = self._get_queryset_for_value(
                        model_cls, value
                    )

    def _get_queryset_for_value(self, model_cls: object, value: object) -> object:
        """Return queryset for a field value."""
        if hasattr(value, "all"):
            pks = [obj.pk for obj in value.all()]
            qs = model_cls.objects.filter(pk__in=pks) | model_cls.objects.all()
        elif isinstance(value, (list, tuple, set)):
            pks = [obj.pk for obj in value]
            qs = model_cls.objects.filter(pk__in=pks) | model_cls.objects.all()
        else:
            qs = model_cls.objects.filter(pk=value.pk) | model_cls.objects.all()
        return qs.distinct()
