"""Viewd for managing parts with module-part link."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect, render

from core.forms import ModulePartFormSet, PartForm
from core.models import Module, Part

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def part_create_view(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    """Handle the creation of a Part instance and its associated ModulePart entries.

    This view is responsible for displaying and processing a form for creating a new
    `Part` object along with a related `ModulePartFormSet`. If the request method
    is POST, the form and formset are validated and saved. Upon successful submission,
    the user is redirected to the part list view. For GET requests, an empty form
    and formset are rendered.
    """
    if pk is not None:
        return part_edit_view(request, pk)

    modules = Module.objects.all()
    next_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or "part_list"
    )
    module_id = request.GET.get("module")
    module_name = None
    if module_id:
        try:
            module_obj = Module.objects.get(pk=module_id)
            module_name = str(module_obj)
        except Module.DoesNotExist:
            module_name = ""
    if request.method == "POST":
        form = PartForm(request.POST)
        formset = ModulePartFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            part = form.save()
            formset.instance = part
            formset.save()
            return redirect(next_url)
    else:
        form = PartForm()
        formset = ModulePartFormSet()
    return render(
        request,
        "core/parts/edit.html",
        {
            "form": form,
            "formset": formset,
            "module_choices": modules,
            "title": "Добавить изделие",
            "submit_label": "Создать",
            "next": next_url,
            "module_id": module_id,
            "module_name": module_name,
        },
    )


def part_edit_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Handle the editing of a Part instance and its associated ModulePart entries.

    This view is responsible for displaying and processing a form for editing an
    existing `Part` object along with a related `ModulePartFormSet`. If the request
    method is POST, the form and formset are validated and saved. Upon successful
    submission, the user is redirected to the part list view. For GET requests,
    the form and formset are pre-populated with the existing data and rendered.
    """
    part = get_object_or_404(Part, pk=pk)
    modules = Module.objects.all()
    next_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or "part_list"
    )

    if request.method == "POST":
        form = PartForm(request.POST, instance=part)
        formset = ModulePartFormSet(request.POST, instance=part)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect(next_url)
    else:
        form = PartForm(instance=part)
        formset = ModulePartFormSet(instance=part)

    return render(
        request,
        "core/parts/edit.html",
        {
            "form": form,
            "formset": formset,
            "module_choices": modules,
            "title": "Редактировать изделие",
            "submit_label": "Сохранить",
            "next": next_url,
        },
    )
