from core.forms.base import BaseStyledForm
from core.models import Part


class PartForm(BaseStyledForm):
    placeholders = {
        "name": "Название",
        "manufacturer": "Производитель",
        "description": "Описание",
        "material": "Материал",
        "manufacture_date": "Дата производства",
    }

    class Meta:
        model = Part
        fields = ("name", "manufacturer", "description", "material", "manufacture_date")
