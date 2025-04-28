from core.models import Machine, Assembly, Part


def create_assembly(data, machine, parent_assembly=None):
    assembly_name = data.get("name", "").strip()

    if not assembly_name:
        return

    assembly = Assembly.objects.create(
        name=assembly_name,
        machine=machine,
        parent_assembly=parent_assembly,
    )

    for part in data.get("parts", []):
        part_name = part.get("name", "").strip()
        if part_name:
            Part.objects.create(
                name=part_name,
                assembly=assembly,
            )

    for sub in data.get("sub_assemblies", []):
        create_assembly(sub, machine, assembly)


def save_machine(machine_data):
    machine = Machine.objects.create(name=machine_data["name"])
    for assembly in machine_data.get("assemblies", []):
        create_assembly(assembly, machine)
    return machine
