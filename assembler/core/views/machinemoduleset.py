"""Views for managing modules with machine-module links."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect, render

from core.forms import MachineModuleFormSet, ModuleForm
from core.models import Machine, Module

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def module_create_view(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    """Handle the creation.

    Of a Module instance and its associated MachinePart entries.
    """
    if pk is not None:
        return module_edit_view(request, pk)

    machines = Machine.objects.all()
    next_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or "module_list"
    )

    machine_id = request.GET.get("machine")
    machine_name = None
    parent_id = request.GET.get("parent")
    parent_name = None
    if parent_id:
        try:
            parent = Module.objects.get(pk=parent_id)
            parent_name = str(parent)
        except Module.DoesNotExist:
            parent_name = ""
    if machine_id:
        try:
            machine_obj = Machine.objects.get(pk=machine_id)
            machine_name = str(machine_obj)
        except Machine.DoesNotExist:
            machine_name = ""
    if request.method == "POST":
        form = ModuleForm(request.POST, request.FILES)
        formset = MachineModuleFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            module = form.save()
            formset.instance = module
            formset.save()
            return redirect(next_url)
    else:
        form = ModuleForm()
        formset = MachineModuleFormSet()

    return render(
        request,
        "core/modules/edit.html",
        {
            "form": form,
            "formset": formset,
            "machine_choices": machines,
            "title": "Добавить модуль",
            "submit_label": "Создать",
            "next": next_url,
            "machine_id": machine_id,
            "machine_name": machine_name,
            "parent_module_id": parent_id,
            "parent_module_name": parent_name,
        },
    )


def module_edit_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Handle the editing.

    Of a Module instance and its associated MachineModule entries.
    """
    module = get_object_or_404(Module, pk=pk)
    machines = Machine.objects.all()
    next_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or "module_list"
    )

    if request.method == "POST":
        form = ModuleForm(request.POST, request.FILES, instance=module)
        formset = MachineModuleFormSet(request.POST, request.FILES, instance=module)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect(next_url)
    else:
        form = ModuleForm(instance=module)
        formset = MachineModuleFormSet(instance=module)
    return render(
        request,
        "core/modules/edit.html",
        {
            "form": form,
            "formset": formset,
            "machine_choices": machines,
            "title": "Редактировать модуль",
            "submit_label": "Сохранить",
            "next": next_url,
        },
    )
