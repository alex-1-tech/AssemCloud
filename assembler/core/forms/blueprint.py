from core.forms.base import BaseStyledForm
from core.models import Blueprint


class BlueprintForm(BaseStyledForm):
    class Meta:
        model = Blueprint
        fields = (
            "weight", "scale", "version", "naming_scheme",
            "developer", "validator", "lead_designer",
            "chief_designer", "approver", "manufacturer",
            "scheme_file", "step_file"
        )

    placeholders = {
        "weight": "Масса в кг",
        "scale": "Например: 1:10",
        "version": "v1.0",
        "naming_scheme": "Схема наименования",
        "scheme_file": "PDF файл чертежа",
        "step_file": "STEP файл модели",
    }
