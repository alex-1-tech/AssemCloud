from core.forms.base import BaseStyledForm
from core.models import Module


class ModuleForm(BaseStyledForm):
    class Meta:
        model = Module
        fields = (
            "machine", "blueprint", "part_number", "serial", "name",
            "parent", "version", "description", "module_status"
        )

    placeholders = {
        "part_number": "Артикул",
        "serial": "Серийный номер",
        "name": "Название модуля",
        "version": "Версия",
        "description": "Описание",
    }
