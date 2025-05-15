"""Module for building and printing a hierarchical assembly tree.

Assembly tree of machines, modules, submodules, and parts.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)
def build_machine_tree(machine: object) -> dict[str, object | list[dict[str, object]]]:
    """Build a tree of modules and parts for a given machine.

    Fetches all modules related to the machine, including nested submodules and parts,
    and organizes them into a hierarchical structure starting from root modules.
    """
    modules = (
        machine.modules.select_related("parent")
        .prefetch_related(
            "module_parts__part",
            "submodules__module_parts__part",
            "submodules__submodules",
        )
        .all()
    )

    root_modules = [m for m in modules if m.parent is None]

    return {
        "machine": machine,
        "modules": [build_module_tree(m) for m in root_modules],
    }


def build_module_tree(module: object) -> dict[str, object | list[dict[str, object]]]:
    """Build a tree of submodules and parts for a single module.

    Recursively processes submodules and their parts, constructing
    a nested structure representing the module hierarchy.
    """
    submodules = (
        module.submodules.select_related("parent")
        .prefetch_related(
            "module_parts__part",
            "submodules__module_parts__part",
            "submodules__submodules",
        )
        .all()
    )

    def build_submodule_node(
            submodule: object,
        ) -> dict[str, object | list[dict[str, object]]]:
        parts = [
            {"part": mp.part, "quantity": mp.quantity}
            for mp in submodule.module_parts.all()
        ]

        subsubmodules = [
            build_submodule_node(subsubmodule)
            for subsubmodule in submodule.submodules.all()
        ]

        return {
            "module": submodule,
            "parts": parts,
            "submodules": subsubmodules,
        }

    return {
        "module": module,
        "submodules": [build_submodule_node(sm) for sm in submodules],
    }


def print_assembly_tree(tree: dict[str, Any], indent: int = 0) -> None:
    """Print the modules and parts tree in a readable format."""
    if indent == 0:
        # Top-level print, can be customized if needed
        pass

    for module_node in tree.get("modules", []):
        logger.info(
            logger.info("%sModule: %s", " " * indent, module_node["module"].name),
        )

        for part_info in module_node.get("parts", []):
            logger.info(
                "%sPart: %s, Quantity: %s",
                " " * (indent + 4),
                part_info["part"].name,
                part_info["quantity"],
            )
        for submodule in module_node.get("submodules", []):
            print_assembly_tree({"modules": [submodule]}, indent + 4)
