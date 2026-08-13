from django.utils.functional import Promise

from core.models import Model, Scheme
from core.schemes import KALMAR32_SCHEME_V1
from core.schemes.models_registry import EQUIPMENT_MODELS_REGISTRY


def stringify_lazy(obj):
    """Рекурсивно преобразует lazy-переводы Django (__proxy__) в обычные строки для JSON."""
    if isinstance(obj, Promise):
        return str(obj)
    if isinstance(obj, dict):
        return {k: stringify_lazy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [stringify_lazy(item) for item in obj]
    return obj


def sync_models_and_schemes() -> None:
    """Synchronize models registry and attaches default JSON schemes."""
    for entry in EQUIPMENT_MODELS_REGISTRY:
        Model.objects.get_or_create(
            name=entry["name"],
            version=entry["version"],
            type_rail=entry.get("type_rail", "NONE"),
            defaults={"is_active": True},
        )

        # Связываем Kalmar32 v1 схему для экземпляров kalmar32
        if entry["name"] == "kalmar32":
            Scheme.objects.update_or_create(
                model_name=entry["name"],
                version=1,
                defaults={
                    "fields_description": stringify_lazy(KALMAR32_SCHEME_V1),
                    "is_latest": True,
                },
            )
