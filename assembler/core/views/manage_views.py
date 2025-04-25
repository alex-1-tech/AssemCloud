from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json

from core.models import Machine
from core.services.save_machine import save_machine

class ManageObjectsView(TemplateView):
    template_name = 'core/manage_objects.html'


@method_decorator(csrf_exempt, name='dispatch')
class SaveAllObjectsView(TemplateView):
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        machine_data = payload.get('machine')
        save_machine(machine_data)
        return JsonResponse({'status': 'success'})
