from django.http import JsonResponse
from django.views import View

from core.models import EquipmentType, Model, RailType


class AllVersionsView(View):
    def get(self, request):
        result = {}
        equipment_types = EquipmentType.objects.filter(is_active=True)

        for eq_type in equipment_types:
            variants = Model.objects.filter(equipment_type=eq_type, is_active=True)
            variant_list = []

            for model in variants:
                item = {"version": model.version}
                if model.type_rail != RailType.NONE:
                    item["type_rail"] = model.type_rail
                variant_list.append(item)

            result[eq_type.name] = {
                "fields": {
                    "title": eq_type.title,
                    "description": eq_type.description,
                    "installer_path": eq_type.installer_path,
                },
                "variants": variant_list,
            }

        return JsonResponse(result)
