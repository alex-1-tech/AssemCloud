from django import forms


class BaseStyledForm(forms.ModelForm):
    placeholders = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, text in self.placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs["placeholder"] = text

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
