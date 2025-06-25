from __future__ import annotations

import logging
from typing import Any

from core.models import MachineModule, Module

logger = logging.getLogger(__name__)


def build_machine_tree(machine: object) -> dict[str, Any]:
    """Build a hierarchical tree for a Machine."""
    root_links = (
        machine.machine_modules
        .filter(parent_module__isnull=True)
        .select_related("module")
    )
    return {
        "machine": machine,
        "modules": [
            build_module_tree(link.module, visited=set(), link=link)
            for link in root_links
        ],
    }


def build_module_tree(
    module: Module,
    visited: set[int] | None = None,
    link: MachineModule | None = None,
) -> dict[str, Any]:
    """Рекурсивно строит узел иерархии для одного модуля."""
    # Если уже были в этом модуле — обрываем ветвь
    if visited is None:
        visited = set()
    if module.pk in visited:
        return {
            "module": module,
            "quantity": link.quantity if link else None,
            "link_id": link.pk if link else None,
            "parts": [],
            "submodules": [],
            "note": "cycle_detected",
        }

    visited.add(module.pk)

    # Собираем детали текущего модуля
    parts: list[dict[str, Any]] = [
    {
        "part": mp.part,
        "quantity": mp.quantity,
        "link_id": mp.pk,
    }
    for mp in module.module_parts.select_related("part").all()
]

    # Собираем дочерние модули: все MachineModule, где parent_module == текущий
    child_links = (
        MachineModule.objects
        .filter(parent_module=module)
        .select_related("module")
    )

    submodules: list[dict[str, Any]] = []
    for child_link in child_links:
        node = build_module_tree(
            child_link.module,
            visited,
            link=child_link,
        )
        submodules.append(node)

    return {
        "module": module,
        "quantity": link.quantity if link else None,
        "link_id": link.pk if link else None,
        "parts": parts,
        "submodules": submodules,
    }
