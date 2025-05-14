def build_machine_tree(machine):
    """
    Строит дерево модулей и деталей с сохранением объектов.
    """
    # Загружаем все модули машины с их деталями и подмодулями с минимизацией количества запросов
    modules = (
        machine.modules
        .select_related("parent")
        .prefetch_related("module_parts__part", "submodules__module_parts__part", "submodules__submodules")
        .all()
    )

    # Рекурсивная функция для построения узла дерева модуля
    def build_module_node(module):
        parts = [
            {"part": mp.part, "quantity": mp.quantity}
            for mp in module.module_parts.all()
        ]

        submodules = [
            build_module_node(submodule)
            for submodule in module.submodules.all()
        ]

        return {
            "module": module,
            "parts": parts,
            "submodules": submodules,
        }

    # Найти корневые модули (не вложенные)
    root_modules = [m for m in modules if m.parent is None]

    return {
        "machine": machine,  # объект Machine
        "modules": [build_module_node(m) for m in root_modules],
    }


def build_module_tree(module):
    """
    Строит дерево подмодулей и деталей для одного модуля.
    """
    # Загружаем все подмодули с их деталями и подмодулями с минимизацией количества запросов
    submodules = (
        module.submodules  # Получаем подмодули для текущего модуля
        .select_related("parent")
        .prefetch_related("module_parts__part", "submodules__module_parts__part", "submodules__submodules")
        .all()
    )

    # Рекурсивная функция для построения узла дерева подмодуля
    def build_submodule_node(submodule):
        parts = [
            {"part": mp.part, "quantity": mp.quantity}
            for mp in submodule.module_parts.all()
        ]

        subsubmodules = [
            build_submodule_node(subsubmodule)
            for subsubmodule in submodule.submodules.all()  # Используем 'submodules' для подмодулей
        ]

        return {
            "module": submodule,
            "parts": parts,
            "submodules": subsubmodules,
        }

    # Строим дерево подмодулей
    return {
        "module": module,  # объект Module
        "submodules": [build_submodule_node(sm) for sm in submodules],
    }

def print_assembly_tree(tree, indent=0):
    """
    Печатает дерево модулей и деталей в читаемом виде.
    """
    prefix = " " * indent
    if indent == 0:
        print(f"Машина: {tree['machine'].name}")

    for module_node in tree["modules"]:
        module = module_node["module"]
        print(f"{prefix}└─ Модуль: {module.name} (id={module.id})")

        # Выводим детали
        for part_info in module_node["parts"]:
            part = part_info["part"]
            quantity = part_info["quantity"]
            print(f"{prefix}   ├─ Деталь: {part.name} (x{quantity}) [id={part.id}]")

        # Рекурсивно выводим подмодули
        if module_node["submodules"]:
            for submodule in module_node["submodules"]:
                print_assembly_tree({"modules": [submodule]}, indent + 4)
