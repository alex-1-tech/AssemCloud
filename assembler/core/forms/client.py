from core.forms.base import BaseStyledForm
from core.models import Client


class ClientForm(BaseStyledForm):
    class Meta:
        model = Client
        fields = ("name", "country", "phone")

    placeholders = {
        "name": "Название клиента",
        "country": "Страна",
        "phone": "+79991234567",
    }
