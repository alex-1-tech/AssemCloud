from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, request
from django.views.decorators.http import require_GET

from core.models import Model, Scheme


@staff_member_required
@require_GET
def get_schemes_for_model(request: request) -> JsonResponse:
    """Вернуть список схем для модели (по её base model_name), либо структуру полей схемы."""
    model_id = request.GET.get("model_id")
    scheme_id = request.GET.get("scheme_id")

    if model_id:
        model_instance = Model.objects.filter(id=model_id).only("equipment_type").first()
        if not model_instance:
            return JsonResponse({"schemes": []})
        schemes = Scheme.objects.filter(equipment_type=model_instance.equipment_type).order_by("-version")
        data = [{"id": s.id, "name": f"v{s.version}" + (" (latest)" if s.is_latest else "")} for s in schemes]
        return JsonResponse({"schemes": data})

    if scheme_id:
        try:
            scheme = Scheme.objects.get(id=scheme_id)
        except Scheme.DoesNotExist:
            return JsonResponse({"error": "Scheme not found"}, status=404)
        return JsonResponse({"fields_description": scheme.fields_description})

    return JsonResponse({"error": "Invalid params"}, status=400)
