"""Parsing services for importing machine modules and their components from XLSX files.

This module provides two main functions:
- `parse_machine`: Import top-level modules and associate them with a machine.
- `parse_module`: Import submodules and parts and associate them with a parent module.

Expected XLSX columns:
- ITEM/ ПОЗ.         (ignored)
- NUMBER/ ОБОЗНАЧЕНИЕ  -> decimal number (used as module/part identifier)
- DESCRIPTION/ ОПИСАНИЕ -> full name/description
- Q-TY/ К-ВО           -> quantity
- CHAPT./ РАЗДЕЛ       -> chapter (used to distinguish parts vs modules)

All column headers may be in English or Cyrillic and may contain slashes.
"""

from __future__ import annotations

import pandas as pd
from django.db import transaction

from core.models import Machine, MachineModule, Module, ModulePart, Part


def normalize_str(value: str | None) -> str:
    """Clean string by stripping whitespace and removing line breaks."""
    return (value or "").strip().replace("\n", "")


def parse_quantity(value: str | None) -> int:
    """Convert quantity value from string to integer."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 1


def validate_columns(df: pd.DataFrame, required: list[str]) -> None:
    """Ensure that all required columns are present in the DataFrame."""
    for col in required:
        if col not in df.columns:
            msg = f'Column "{col}" is missing in the XLSX file.'
            raise ValueError(msg)


def read_xlsx(file: object) -> pd.DataFrame:
    """Read XLSX file into a DataFrame and normalize column names.

    Takes the first part of each column before "/" and lowercases it.
    """
    df = pd.read_excel(file, dtype=str)
    df.columns = [col.split("/")[0].strip().lower() for col in df.columns]
    return df


def parse_machine(xlsx_file: object, machine: Machine) -> dict[str, int]:
    """Parse top-level modules from an XLSX file.

    Returns a dictionary with counts of created and updated objects.
    """
    df = read_xlsx(xlsx_file)
    validate_columns(df, ["number", "description", "q-ty", "chapt."])

    created = 0
    updated = 0

    with transaction.atomic():
        for _, row in df.iterrows():
            decimal = normalize_str(row.get("number"))
            name = normalize_str(row.get("description"))[:25]
            description = normalize_str(row.get("description"))
            chapter = normalize_str(row.get("chapt.")).lower()
            quantity = parse_quantity(row.get("q-ty"))

            if "others" in chapter or "stand. parts" in chapter:
                msg = "'Stand. parts' or 'others' should be parsed with module, not machine."
                raise ValueError(msg)
            if not decimal:
                msg = "Module must have a decimal number."
                raise ValueError(msg)
            module, created_flag = Module.objects.update_or_create(
                decimal=decimal,
                defaults={"name": name, "description": description},
            )

            link, updated_flag = MachineModule.objects.update_or_create(
                machine=machine,
                module=module,
                defaults={"quantity": quantity},
            )

            if created_flag:
                created += 1
            if updated_flag:
                updated += 1

    return {
        "modules_created": created,
        "links_created_or_updated": updated,
    }


def parse_module(xlsx_file: object, parent_module: Module) -> dict[str, int]:
    """Parse submodules and parts from an XLSX file and attach them to the given parent module.

    Uses chapter field to distinguish parts ("others", "stand. parts") from nested modules.
    """
    df = read_xlsx(xlsx_file)
    validate_columns(df, ["number", "description", "q-ty", "chapt."])

    created = 0
    updated = 0

    with transaction.atomic():
        for _, row in df.iterrows():
            decimal = normalize_str(row.get("number"))
            description = normalize_str(row.get("description"))
            max_name_length = 15
            if "(" in description and description.index("(") > max_name_length:
                name = normalize_str(description).split("(")[0].strip()
            else:
                name = normalize_str(description)[:25]
            chapter = normalize_str(row.get("chapt.")).lower()
            quantity = parse_quantity(row.get("q-ty"))

            if "others" in chapter or "stand. parts" in chapter:
                if decimal is None or decimal == "":
                    part, part_created = Part.objects.update_or_create(
                        description=description,
                        defaults={"name": name, "decimal": decimal},
                    )
                else:
                    part, part_created = Part.objects.update_or_create(
                        decimal=decimal,
                        defaults={"name": name, "description": description},
                    )
                link, link_created = ModulePart.objects.update_or_create(
                    module=parent_module,
                    part=part,
                    defaults={"quantity": quantity},
                )
            else:
                module, mod_created = Module.objects.update_or_create(
                    decimal=decimal,
                    defaults={"name": name, "description": description},
                )
                link, link_created = MachineModule.objects.update_or_create(
                    parent_module=parent_module,
                    module=module,
                    defaults={"quantity": quantity},
                )

            if ("part_created" in locals() and part_created) or (
                "mod_created" in locals() and mod_created
            ):
                created += 1
            if link_created:
                updated += 1

    return {
        "modules_created": created,
        "links_created_or_updated": updated,
    }
