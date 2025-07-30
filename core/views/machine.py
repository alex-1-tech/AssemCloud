"""Views for managing Machine objects and their related Converters.

This module provides class-based views for listing, creating, updating, deleting,
duplicating, and exporting Machine instances,
along with handling associated Converter objects.
"""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.db.models import Q, QuerySet
from django.forms.models import inlineformset_factory
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)
from weasyprint import CSS, HTML

from core.forms import (
    ConverterForm,
    MachineDuplicateForm,
    MachineForm,
)
from core.mixins import NextUrlMixin, QuerySetMixin
from core.models import Converter, Machine

MACHINE_LIST_URL = "machine_list"

# Inline formset for converters
ConverterFormSet = inlineformset_factory(
    Machine,
    Converter,
    form=ConverterForm,
    extra=1,
    can_delete=True,
)


def get_field_categories_for_machine(machine: Machine) -> list[dict[str, Any]]:
    """Return a list of field categories for a given machine."""
    return [
        {
            "name": "Основная информация",
            "fields": [
                ("Серийный номер", machine.serial_number),
                ("ПО", f"{machine.software} v{machine.software_version}"),
            ],
        },
        {
            "name": "Зарядка и питание",
            "fields": [
                ("Зарядка планшета (напряжение)", machine.tablet_charger_voltage),
                ("Модель зарядного устройства", machine.charger_model),
                ("Напряжение зарядного устройства", machine.charger_voltage),
                ("Ток зарядного устройства", machine.charger_current),
                ("Адаптер питания", machine.power_adapter),
            ],
        },
        {
            "name": "Аккумулятор",
            "fields": [
                ("Напряжение батареи", machine.battery_voltage),
                ("Ёмкость батареи", machine.battery_capacity),
                ("Серийный номер батареи", machine.battery_serial),
            ],
        },
        {
            "name": "УЗК и драйверы",
            "fields": [
                ("Тип УЗК", machine.uzk_type),
                ("Серийный номер УЗК", machine.uzk_serial),
                ("Производитель УЗК", machine.uzk_manufacturer),
                ("Тип драйвера", machine.driver_type),
                ("Серийный номер драйвера", machine.driver_serial),
                ("Серийный номер SOC", machine.soc_serial),
            ],
        },
        {
            "name": "Кабели и шасси",
            "fields": [
                ("Тип наконечника кабеля", machine.cable_tip),
                ("Тип рамы шасси", machine.chassis_type),
                ("Версия исполнения РСП", machine.rsp_version),
            ],
        },
        {
            "name": "Сканер",
            "fields": [
                ("Тип сканера", machine.scanner_type),
                ("Версия сканера", machine.scanner_version),
            ],
        },
        {
            "name": "Планшет",
            "fields": [
                ("Фирма", machine.tablet_brand),
                ("Модель", machine.tablet_model),
                ("Серийный номер", machine.tablet_serial),
                ("ОС", machine.tablet_os),
                ("DRIVER1", machine.tablet_driver1),
                ("Версия DRIVER1", machine.tablet_driver1_version),
                ("DRIVER2", machine.tablet_driver2),
                ("Версия DRIVER2", machine.tablet_driver2_version),
            ],
        },
        {
            "name": "Системная информация",
            "fields": [
                ("Дата создания", machine.created_at.strftime("%d.%m.%Y %H:%M")),
                ("Дата изменения", machine.updated_at.strftime("%d.%m.%Y %H:%M")),
            ],
        },
    ]


class MachinePDFView(View):
    """Generate a PDF with machine details styled as a detail view."""

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Handle GET request to generate and return a PDF for the specified machine."""
        machine = get_object_or_404(Machine, pk=pk)

        context: dict[str, Any] = {
            "title": "Машина",
            "subtitle": (
                f"{machine.serial_number} - "
                f"{machine.software} v{machine.software_version}"
            ),
            "field_categories": get_field_categories_for_machine(machine),
            "converters": machine.converters.all(),
            "machine": machine,
        }

        html_string: str = render_to_string("core/machines/detail_pdf.html", context)
        base_url: str = request.build_absolute_uri("/")

        html = HTML(string=html_string, base_url=base_url)
        css = CSS(string=self.get_pdf_styles())
        pdf: bytes = html.write_pdf(stylesheets=[css])

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="machine_{machine.serial_number}.pdf"'
        )
        return response

    def get_pdf_styles(self) -> str:
        """Return compact CSS styles for PDF rendering."""
        return """
            @font-face {
                font-family: 'DejaVu Sans';
                src: url('/static/fonts/DejaVuSans.ttf');
            }
            body {
                font-family: 'DejaVu Sans', sans-serif;
                font-size: 9pt;
                line-height: 1.3;
                color: #333;
                padding: 10px;
                margin: 0;
            }
            .container {
                max-width: 100%;
            }
            .header {
                text-align: center;
                margin-bottom: 10px;
                padding-bottom: 5px;
            }
            h1 {
                font-size: 14pt;
                margin: 0 0 2px 0;
            }
            .subtitle {
                font-size: 10pt;
                color: #666;
                margin: 0;
            }
            .category {
                margin-bottom: 8px;
                page-break-inside: avoid;
            }
            .category-title {
                font-size: 10pt;
                font-weight: bold;
                border-bottom: 1px solid #ddd;
                padding-bottom: 2px;
                margin-bottom: 5px;
            }
            .row {
                display: flex;
                flex-wrap: wrap;
                margin: 0 -5px;
            }
            .field {
                flex: 0 0 50%;
                max-width: 50%;
                padding: 0 5px;
                margin-bottom: 5px;
                box-sizing: border-box;
            }
            .field-label {
                font-weight: bold;
                min-width: 110px;
                display: inline-block;
            }
            .converters-section {
                margin-top: 8px;
            }
            .converters-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 8pt;
                margin-top: 5px;
            }
            .converters-table th,
            .converters-table td {
                border: 1px solid #ddd;
                padding: 4px 6px;
                text-align: left;
            }
            .converters-table th {
                background-color: #f8f9fa;
                font-weight: bold;
            }
            .footer {
                margin-top: 10px;
                padding-top: 5px;
                border-top: 1px solid #eee;
                font-size: 8pt;
                color: #777;
                display: flex;
                justify-content: space-between;
            }
        """


class MachineListView(QuerySetMixin, ListView):
    """Display a list of all machines."""

    model = Machine
    template_name = "core/list.html"
    context_object_name = "machines"
    paginate_by = 7

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the machine list, filtered by search query."""
        q: str = self.request.GET.get("q", "").strip()
        base_q: Q = Q(
            Q(serial_number__icontains=q)
            | Q(software__icontains=q)
            | Q(uzk_serial__icontains=q)
            | Q(tablet_model__icontains=q),
        )
        return self.get_queryset_default(q, base_q).order_by("-id")

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Return context data for the machine list view."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Список машин",
                "items": self.get_machine_items(context["machines"]),
                "add_url": reverse("machine_add"),
                "empty_message": (
                    "Ничего не найдено по вашему запросу."
                    if self.request.GET.get("q")
                    else None
                ),
            },
        )
        return context

    def get_machine_items(self, machines: QuerySet) -> list[dict[str, Any]]:
        """Return a list of machine items for display in the list view."""
        return [
            {
                "title": (
                    f"s/n: {m.serial_number} — {m.software} v{m.software_version}"
                ),
                "subtitle": m.uzk_type,
                "view_url": reverse("machine_detail", args=[m.pk]),
                "edit_url": (
                    reverse("machine_edit", args=[m.pk])
                    + f"?next={self.request.get_full_path()}"
                ),
                "delete_confirm_message": f"Удалить машину {m.serial_number}?",
            }
            for m in machines
        ]


class MachineCreateView(NextUrlMixin, CreateView):
    """Create a new machine along with its converters."""

    model = Machine
    form_class = MachineForm
    template_name = "core/edit.html"
    default_redirect_url_name = MACHINE_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Return context data for the machine creation view."""
        ctx = super().get_context_data(**kwargs)
        ctx["converters"] = (
            ConverterFormSet(self.request.POST)
            if self.request.method == "POST"
            else ConverterFormSet()
        )
        return ctx

    def form_valid(self, form: MachineForm) -> HttpResponseRedirect:
        """Handle valid form submission for machine creation."""
        converters = ConverterFormSet(self.request.POST)
        if form.is_valid() and converters.is_valid():
            self.object = form.save()
            converters.instance = self.object
            converters.save()
            messages.success(
                self.request,
                "Машина и преобразователи успешно сохранены.",
            )
            return redirect(self.get_success_url())
        return self.form_invalid(form)


class MachineUpdateView(NextUrlMixin, UpdateView):
    """Edit a machine and its converters."""

    model = Machine
    form_class = MachineForm
    template_name = "core/edit.html"
    default_redirect_url_name = MACHINE_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Return context data for the machine update view."""
        ctx = super().get_context_data(**kwargs)
        ctx["converters"] = (
            ConverterFormSet(self.request.POST, instance=self.object)
            if self.request.method == "POST"
            else ConverterFormSet(instance=self.object)
        )
        return ctx

    def form_valid(self, form: MachineForm) -> HttpResponseRedirect:
        """Handle valid form submission for machine update."""
        converters = ConverterFormSet(self.request.POST, instance=self.object)
        if form.is_valid() and converters.is_valid():
            self.object = form.save()
            converters.instance = self.object
            converters.save()
            messages.success(self.request, "Изменения сохранены.")
            return redirect(self.get_success_url())
        return self.form_invalid(form)


class MachineDetailView(DetailView):
    """Display detailed info about a machine with all fields organized by categories."""

    model = Machine
    template_name = "core/detail.html"
    context_object_name = "machine"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add all machine fields organized by categories to context."""
        machine: Machine = self.object
        context = super().get_context_data(**kwargs)

        field_categories: list[dict[str, Any]] = [
            {
                "name": "Основная информация",
                "fields": [
                    ("Серийный номер", machine.serial_number),
                    ("ПО", f"{machine.software} v{machine.software_version}"),
                ],
            },
            {
                "name": "Зарядка и питание",
                "fields": [
                    ("Зарядка планшета (напряжение)", machine.tablet_charger_voltage),
                    ("Модель зарядного устройства", machine.charger_model),
                    ("Напряжение зарядного устройства", machine.charger_voltage),
                    ("Ток зарядного устройства", machine.charger_current),
                    ("Адаптер питания", machine.power_adapter),
                ],
            },
            {
                "name": "Аккумулятор",
                "fields": [
                    ("Напряжение батареи", machine.battery_voltage),
                    ("Ёмкость батареи", machine.battery_capacity),
                    ("Серийный номер батареи", machine.battery_serial),
                ],
            },
            {
                "name": "УЗК и драйверы",
                "fields": [
                    ("Тип УЗК", machine.uzk_type),
                    ("Серийный номер УЗК", machine.uzk_serial),
                    ("Производитель УЗК", machine.uzk_manufacturer),
                    ("Тип драйвера", machine.driver_type),
                    ("Серийный номер драйвера", machine.driver_serial),
                    ("Серийный номер SOC", machine.soc_serial),
                ],
            },
            {
                "name": "Кабели и шасси",
                "fields": [
                    ("Тип наконечника кабеля", machine.cable_tip),
                    ("Тип рамы шасси", machine.chassis_type),
                    ("Версия исполнения РСП", machine.rsp_version),
                ],
            },
            {
                "name": "Сканер",
                "fields": [
                    ("Тип сканера", machine.scanner_type),
                    ("Версия сканера", machine.scanner_version),
                ],
            },
            {
                "name": "Планшет",
                "fields": [
                    ("Фирма", machine.tablet_brand),
                    ("Модель", machine.tablet_model),
                    ("Серийный номер", machine.tablet_serial),
                    ("ОС", machine.tablet_os),
                    ("DRIVER1", machine.tablet_driver1),
                    ("Версия DRIVER1", machine.tablet_driver1_version),
                    ("DRIVER2", machine.tablet_driver2),
                    ("Версия DRIVER2", machine.tablet_driver2_version),
                ],
            },
            {
                "name": "Системная информация",
                "fields": [
                    ("Дата создания", machine.created_at.strftime("%d.%m.%Y %H:%M")),
                    ("Дата изменения", machine.updated_at.strftime("%d.%m.%Y %H:%M")),
                ],
            },
        ]

        context.update(
            {
                "title": "Машина",
                "subtitle": (
                    f"{machine.serial_number} - "
                    f"{machine.software} v{machine.software_version}"
                ),
                "field_categories": field_categories,
                "converters": machine.converters.all(),
                "edit_url": (
                    reverse("machine_edit", args=[machine.pk])
                    + f"?next={self.request.get_full_path()}"
                ),
                "add_url": reverse("machine_add"),
                "add_label": "Добавить новую машину",
                "pdf_url": reverse("machine_pdf", args=[machine.pk]),
            },
        )
        return context


class MachineDeleteView(NextUrlMixin, DeleteView):
    """Delete a machine."""

    model = Machine
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = MACHINE_LIST_URL

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Return context data for the machine delete confirmation view."""
        machine: Machine = self.object
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "title": "Удалить машину",
                "message": (
                    f"Вы уверены, что хотите удалить машину {machine.serial_number}?"
                ),
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("newmachine_detail", args=[machine.pk]),
            },
        )
        return ctx

    def delete(
        self,
        request: HttpRequest,
        *args: object,
        **kwargs: object,
    ) -> HttpResponseRedirect:
        """Handle machine deletion and display a success message."""
        messages.success(request, "Машина удалена.")
        return super().delete(request, *args, **kwargs)


class MachineDuplicateView(NextUrlMixin, FormView):
    """Duplicate a machine."""

    template_name = "core/duplicate.html"
    form_class = MachineDuplicateForm
    default_redirect_url_name = MACHINE_LIST_URL

    def dispatch(
        self,
        request: HttpRequest,
        *args: object,
        **kwargs: object,
    ) -> object:
        """Handle dispatch for the duplicate view.

        Fetch the original machine if provided.
        """
        self.machine_id: str | None = request.GET.get("machine")
        self.original_machine: Machine | None = (
            get_object_or_404(Machine, pk=self.machine_id) if self.machine_id else None
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        """Return form keyword arguments.

        Include the original machine if available.
        """
        kwargs = super().get_form_kwargs()
        if self.original_machine:
            kwargs["original_machine"] = self.original_machine
        return kwargs

    def form_valid(self, form: MachineDuplicateForm) -> HttpResponseRedirect:
        """Handle valid form submission for machine duplication."""
        new_serial: str = form.cleaned_data["serial_number"]
        messages.success(
            self.request,
            f"Создана копия машины с серийным номером {new_serial}.",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Return context data for the machine duplication view."""
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "title": "Дублировать машину",
                "submit_label": "Дублировать",
            },
        )
        return ctx
