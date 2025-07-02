from __future__ import annotations

import logging
from typing import Any

from core.models import MachineModule, Module

logger = logging.getLogger(__name__)


def build_machine_tree(machine: object) -> dict[str, Any]:
    """Build a hierarchical tree for a Machine."""
    root_links = MachineModule.objects.filter(
        machine=machine,
        parent__isnull=True,
    )
    return {
        "machine": machine,
        "modules": [
            build_submodule_tree(
                link,
            )
            for link in root_links
        ],
    }


def build_module_tree(
    module: Module,
) -> dict[str, Any]:
    """Build a hierarchical tree for a Module."""
    links = MachineModule.objects.filter(
        parent=module,
    )

    return {
        "module": module,
        "submodules": [
            build_submodule_tree(
                link,
            )
            for link in links
        ],
    }


def build_submodule_tree(
    link: MachineModule,
) -> dict[str, Any]:
    """Рекурсивно строит узел иерархии для одного модуля."""
    # Собираем детали текущего модуля
    parts: list[dict[str, Any]] = [
        {
            "part": mp.part,
            "quantity": mp.quantity,
            "link": mp.pk,
        }
        for mp in link.module.module_parts.select_related("part").all()
    ]

    # Собираем дочерние модули: все MachineModule, где parent_module == текущий
    child_links = MachineModule.objects.filter(parent=link.module).select_related(
        "module",
    )

    submodules: list[dict[str, Any]] = []
    for child_link in child_links:
        node = build_submodule_tree(
            link=child_link,
        )
        submodules.append(node)

    return {
        "module": link.module,
        "quantity": link.quantity if link else None,
        "link": link.pk if link else None,
        "parts": parts,
        "submodules": submodules,
    }
