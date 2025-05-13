from core.forms.base import BaseStyledForm
from core.models import Machine


class MachineForm(BaseStyledForm):
    class Meta:
        model = Machine
        fields = ("name", "version", "clients")

    placeholders = {
        "name": "Название машины",
        "version": "Версия машины",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["clients"].widget.attrs.update(
            {"class": "form-select", "multiple": "multiple"}
        )
