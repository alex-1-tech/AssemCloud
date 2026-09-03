from django.db import migrations


def migrate_old_models(apps, schema_editor):
    EquipmentType = apps.get_model("core", "EquipmentType")
    Model = apps.get_model("core", "Model")
    Scheme = apps.get_model("core", "Scheme")
    Equipment = apps.get_model("core", "Equipment")
    Kalmar32 = apps.get_model("core", "Kalmar32")
    Phasar01 = apps.get_model("core", "Phasar01")
    Phasar02 = apps.get_model("core", "Phasar02")

    kalmar_type, _ = EquipmentType.objects.get_or_create(
        name="kalmar32",
        defaults={
            "title": "Kalmar32",
            "description": "Kalmar32 equipment",
            "is_active": True,
        },
    )
    phasar_type, _ = EquipmentType.objects.get_or_create(
        name="phasarsl",
        defaults={
            "title": "Phasar",
            "description": "Phasar equipment (unified)",
            "is_active": True,
        },
    )

    kalmar_model, _ = Model.objects.get_or_create(
        equipment_type=kalmar_type, version="ver_unavailable", type_rail="None", defaults={"is_active": True}
    )
    phasar_model, _ = Model.objects.get_or_create(
        equipment_type=phasar_type, version="Ver_3", type_rail="NONE", defaults={"is_active": True}
    )

    kalmar_scheme = Scheme.objects.filter(equipment_type=kalmar_type, is_latest=True).first()
    if not kalmar_scheme:
        kalmar_scheme = Scheme.objects.create(
            equipment_type=kalmar_type, version=1, is_latest=True, fields_description={}
        )
    else:
        if not kalmar_scheme.is_latest:
            kalmar_scheme.is_latest = True
            kalmar_scheme.save()

    phasar_scheme = Scheme.objects.filter(equipment_type=phasar_type, is_latest=True).first()
    if not phasar_scheme:
        phasar_scheme = Scheme.objects.create(
            equipment_type=phasar_type, version=1, is_latest=True, fields_description={}
        )
    else:
        if not phasar_scheme.is_latest:
            phasar_scheme.is_latest = True
            phasar_scheme.save()

    def copy_equipment(old_instance, model_obj, scheme_obj):
        exclude_fields = {
            "id",
            "serial_number",
            "invoice",
            "packet_list",
            "shipment_date",
            "license",
            "license_password",
        }
        other_data = {}
        for field in old_instance._meta.get_fields():
            if field.name in exclude_fields or field.auto_created:
                continue
            other_data[field.name] = getattr(old_instance, field.name)

        if hasattr(old_instance, "license_password"):
            other_data["license_password"] = old_instance.license_password

        equipment, created = Equipment.objects.get_or_create(
            serial_number=old_instance.serial_number,
            defaults={
                "invoice": old_instance.invoice or "",
                "packet_list": old_instance.packet_list or "",
                "shipment_date": old_instance.shipment_date,
                "license": old_instance.license,
                "model": model_obj,
                "scheme": scheme_obj,
                "other_data": other_data,
            },
        )
        if not created:
            equipment.invoice = old_instance.invoice or ""
            equipment.packet_list = old_instance.packet_list or ""
            equipment.shipment_date = old_instance.shipment_date
            equipment.license = old_instance.license
            equipment.model = model_obj
            equipment.scheme = scheme_obj
            equipment.other_data = other_data
            equipment.save()

        return equipment

    for old in Kalmar32.objects.all():
        copy_equipment(old, kalmar_model, kalmar_scheme)

    for old in Phasar01.objects.all():
        copy_equipment(old, phasar_model, phasar_scheme)

    for old in Phasar02.objects.all():
        copy_equipment(old, phasar_model, phasar_scheme)


def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0037_equipmenttype_alter_model_options_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_old_models, reverse_migration),
    ]
