from __future__ import annotations

from typing import TypedDict


class ModelVariant(TypedDict):
    name: str
    type_rail: str
    version: str


EQUIPMENT_MODELS_REGISTRY: list[ModelVariant] = [
    # KALMAR 32+ / IRS 52
    {"name": "kalmar32", "type_rail": "IRS52", "version": "Ver_3"},
    {"name": "kalmar32", "type_rail": "IRS52", "version": "Ver_4"},
    # KALMAR 32+ / UIC 60
    {"name": "kalmar32", "type_rail": "UIC60", "version": "Ver_1"},
    {"name": "kalmar32", "type_rail": "UIC60", "version": "Ver2 Plant"},
    {"name": "kalmar32", "type_rail": "UIC60", "version": "Ver_3"},
    {"name": "kalmar32", "type_rail": "UIC60", "version": "Ver_4"},
    # KALMAR 32+ / R 65
    {"name": "kalmar32", "type_rail": "R65", "version": "Ver_4"},
    # FAZAR 01 (SL)
    {"name": "phasarsl", "version": "Ver_1"},
    {"name": "phasarsl", "version": "Ver_2"},
    # FAZAR 02 (DL)
    {"name": "phasardl", "version": "Ver_1"},
    {"name": "phasardl","version": "Ver_2"},
    # CHAMELEON 32+
    {"name": "chameleon32", "version": "Ver_1"},
    {"name": "chameleon32", "version": "Ver_2"},
]


def get_version_choices_for_model(model_name: str, rail_type: str | None = None) -> list[tuple[str, str]]:
    """Возвращает кортежи (value, label) для Django choice s по модели и типу рельса."""
    versions = set()
    for item in EQUIPMENT_MODELS_REGISTRY:
        if item["name"] == model_name and (rail_type is None or item["type_rail"] == rail_type):
            versions.add(item["version"])

    return sorted([(ver, ver) for ver in versions])
