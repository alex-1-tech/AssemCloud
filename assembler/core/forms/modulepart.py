from core.forms.base import BaseStyledForm
from core.models import ModulePart


class ModulePartForm(BaseStyledForm):
    placeholders = {
        "module": "Модуль",
        "part": "Деталь",
        "quantity": "Количество",
    }

    class Meta:
        model = ModulePart
        fields = ("module", "part", "quantity")
