"""Module for building and printing a hierarchical assembly tree.

Assembly tree of machines, modules, submodules, and parts.
"""

from __future__ import annotations

import logging

from core.models import Module

logger = logging.getLogger(__name__)


def build_machine_tree(machine: object) -> dict[str, object | list[dict[str, object]]]:
    """Build a tree of modules and parts for a given machine.

    Fetches all modules related to the machine, including nested submodules and parts,
    and organizes them into a hierarchical structure starting from root modules.
    """
    modules = [
        {
            "module": module.module,
            "quantity": module.quantity,
            "parent_module": module.parent_module,
            "id": module.pk,
        }
        for module in machine.machine_modules.select_related("module").all()
    ]
    root_modules = [m for m in modules if m["parent_module"] is None]

    return {
        "machine": machine,
        "modules": [build_module_tree(m) for m in root_modules],
    }


def build_module_tree(modules: object) -> dict[str, object | list[dict[str, object]]]:
    """Build a tree of submodules and parts for a single module.

    Recursively processes submodules and their parts, constructing
    a nested structure representing the module hierarchy.
    """
    if isinstance(modules, Module):
        modules = {
            "module": modules,
            "parent_module": None,
            "id": modules.pk,
        }
    submodules = [
        {
            "module": module.module,
            "quantity": module.quantity,
            "parent_module": module.parent_module,
            "id": module.pk,
        }
        for module in modules["module"].parent_modules.select_related("module").all()
    ]
    parts = [
        {
            "part": mp.part,
            "quantity": mp.quantity,
            "id": mp.pk,
        }
        for mp in modules["module"].module_parts.all()
    ]

    def build_submodule_node(
        submodule: object,
    ) -> dict[str, object | list[dict[str, object]]]:
        parts_sub = [
            {
                "part": mp.part,
                "quantity": mp.quantity,
                "id": mp.pk,
            }
            for mp in submodule["module"].module_parts.all()
        ]

        subsubmodules = [
            {
                "module": module.module,
                "quantity": module.quantity,
                "parent_module": module.parent_module,
                "id": module.pk,
            }
            for module in submodule["module"]
            .parent_modules.select_related("module")
            .all()
        ]

        return {
            "module": submodule,
            "parts": parts_sub,
            "submodules": [build_submodule_node(sm) for sm in subsubmodules],
        }

    return {
        "module": modules,
        "parts": parts,
        "submodules": [build_submodule_node(sm) for sm in submodules],
    }
