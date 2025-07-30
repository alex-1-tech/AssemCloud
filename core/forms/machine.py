"""Forms for Machine and Converter entities."""

from __future__ import annotations

from typing import ClassVar

from django.forms import DateInput, ModelForm
from django.forms.models import inlineformset_factory
from django_select2.forms import ModelSelect2Widget, Select2Widget

from core.forms.base import BaseStyledForm
from core.models import Converter, Machine


class MachineForm(BaseStyledForm):
    """Form for creating or updating a Machine instance."""

    placeholders: ClassVar[dict[str, str]] = {
        "serial_number": "Например: 0083",
        "software_version": "Например: 4",
        "charger_voltage": "Например: 16.8V",
        "charger_current": "Например: 5A",
        "battery_capacity": "Например: 24А/ч",
        "battery_serial": "Например: 25013",
        "uzk_serial": "Например: 25034",
        "driver_serial": "Например: AA43399",
        "soc_serial": "Например: 0074f538",
        "tablet_model": "Например: Latitude 7230",
        "tablet_brand": "Например: DELL",
        "tablet_serial": "Например: 3FFRYY3",
        "tablet_os": "Например: Windows 11",
        "tablet_driver1": "Например: Intel(R) Ethernet Connection (16) I219-LM",
        "tablet_driver1_version": "Например: 12.19.2.62",
        "tablet_driver2": "Например: Intel(R) Wi-Fi 6E AX211 160MHz",
        "tablet_driver2_version": "Например: 23.120.0.3",
    }

    class Meta:
        """Meta options for MachineForm."""

        model = Machine
        fields: ClassVar[list[str]] = [
            # Основная информация
            "serial_number",
            # ПО
            "software",
            "software_version",
            # Зарядка
            "tablet_charger_voltage",
            # Зарядное устройство
            "charger_model",
            "charger_voltage",
            "charger_current",
            # Адаптер питания
            "power_adapter",
            # Аккумулятор
            "battery_voltage",
            "battery_capacity",
            "battery_serial",
            # УЗК и драйверы
            "uzk_type",
            "uzk_serial",
            "uzk_manufacturer",
            "driver_type",
            "driver_serial",
            "soc_serial",
            # Кабели и шасси
            "cable_tip",
            "chassis_type",
            "rsp_version",
            # Сканер
            "scanner_type",
            "scanner_version",
            # Планшет
            "tablet_model",
            "tablet_brand",
            "tablet_serial",
            "tablet_os",
            "tablet_driver1",
            "tablet_driver1_version",
            "tablet_driver2",
            "tablet_driver2_version",
        ]
        widgets: ClassVar[dict[str, object]] = {
            "software": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "charger_model": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "power_adapter": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "battery_voltage": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "uzk_type": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "uzk_manufacturer": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "driver_type": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "cable_tip": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "chassis_type": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "rsp_version": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "scanner_type": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
            "scanner_version": Select2Widget(
                attrs={"data-minimum-results-for-search": "Infinity"},
            ),
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize MachineForm and set placeholders and widget styles."""
        super().__init__(*args, **kwargs)

        # Плейсхолдеры
        for fname, ph in self.placeholders.items():
            if fname in self.fields:
                self.fields[fname].widget.attrs["placeholder"] = ph

        # Отстройка Select2-виджетов
        for field in self.fields.values():
            if isinstance(field.widget, Select2Widget):
                field.widget.attrs.update({"style": "width: 100%; min-height: 40px;"})


class ConverterForm(ModelForm):
    """Form for one Converter."""

    class Meta:
        """Meta options for ConverterForm."""

        model = Converter
        fields: ClassVar[tuple[str, ...]] = (
            "type",
            "serial",
            "frequency",
            "release_date",
            "connector_type",
        )
        widgets: ClassVar[dict[str, object]] = {
            "release_date": DateInput(attrs={"type": "date"}),
        }


# Inline-formset для Converter внутри NewMachine
ConverterFormSet = inlineformset_factory(
    Machine,
    Converter,
    form=ConverterForm,
    extra=1,
    can_delete=True,
)


class MachineDuplicateForm(BaseStyledForm):
    """Form for duplicating a Machine instance."""

    placeholders: ClassVar[dict[str, str]] = {
        "serial_number": "Новый серийный номер машины",
    }

    class Meta:
        """Meta options for MachineDuplicateForm."""

        model = Machine
        fields: ClassVar[tuple[str, ...]] = ("serial_number",)
        widgets: ClassVar[dict[str, object]] = {
            "original_machine": ModelSelect2Widget(
                model=Machine,
                search_fields=["serial_number__icontains"],
                attrs={"style": "width: 100%; min-height: 40px;"},
            ),
        }

    def __init__(
        self,
        *args: object,
        original_machine: Machine | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize MachineDuplicateForm and set placeholders and initial value."""
        super().__init__(*args, **kwargs)
        if original_machine:
            self.fields["original_machine"].initial = original_machine

        # Плейсхолдер
        if "serial_number" in self.fields:
            self.fields["serial_number"].widget.attrs["placeholder"] = (
                self.placeholders["serial_number"]
            )
