from django import forms

from core.models import Manufacturer


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ("name", "country", "language", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            "name": "Название",
            "country": "Страна",
            "language": "ru",
            "phone": "+79991234567",
        }

        for name, text in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs["placeholder"] = text

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
