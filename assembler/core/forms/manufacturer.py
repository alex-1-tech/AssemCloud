from core.forms.base import BaseStyledForm
from core.models import Manufacturer


class ManufacturerForm(BaseStyledForm):
    placeholders = {
        "name": "Название",
        "country": "Страна",
        "language": "ru",
        "phone": "+79991234567",
    }

    class Meta:
        model = Manufacturer
        fields = ("name", "country", "language", "phone")
