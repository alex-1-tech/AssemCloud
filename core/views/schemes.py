from django.http import JsonResponse
from django.views import View

from core.models import Scheme


class AllSchemesExportView(View):
    def get(self, request):
        schemes = Scheme.objects.select_related("equipment_type").all()
        result = {}

        for scheme in schemes:
            eq_name = scheme.equipment_type.name
            if eq_name not in result:
                result[eq_name] = []

            fields_desc = scheme.fields_description.copy() if scheme.fields_description else {"sections": []}

            sections = fields_desc.get("sections", [])
            if not isinstance(sections, list):
                sections = []

            registration_section = {
                "title": "Registration data",
                "fields": [
                    {
                        "name": "serial_number",
                        "label": "Serial number",
                        "cpp_name": "serialNumber",
                        "type": "string"
                    },
                    {
                        "name": "shipment_date",
                        "label": "Shipment date",
                        "cpp_name": "shipmentDate",
                        "type": "date"
                    },
                    {
                        "name": "invoice",
                        "label": "Invoice",
                        "cpp_name": "invoice",
                        "type": "string"
                    },
                    {
                        "name": "packet_list",
                        "label": "Packet list",
                        "cpp_name": "packetList",
                        "type": "string"
                    }
                ]
            }

            sections = [s for s in sections if s.get("title") != "Registration data"]
            sections.insert(0, registration_section)
            fields_desc["sections"] = sections

            scheme_data = {
                "title": f"{scheme.equipment_type.title} Specification Scheme v{scheme.version}",
                "model": eq_name,
                "version": scheme.version,
                "sections": sections,
            }

            result[eq_name].append(scheme_data)

        return JsonResponse(result)