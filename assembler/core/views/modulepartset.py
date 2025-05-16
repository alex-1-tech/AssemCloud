"""Viewd for managing parts with module-part link."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from core.forms import ModulePartFormSet, PartForm
from core.models import Module


def part_create_view(request: HttpRequest) -> HttpResponse:
    """Handle the creation of a Part instance and its associated ModulePart entries.

    This view is responsible for displaying and processing a form for creating a new
    `Part` object along with a related `ModulePartFormSet`. If the request method
    is POST, the form and formset are validated and saved. Upon successful submission,
    the user is redirected to the part list view. For GET requests, an empty form
    and formset are rendered.
    """
    modules = Module.objects.all()
    if request.method == "POST":
        form = PartForm(request.POST)
        formset = ModulePartFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            part = form.save()
            formset.instance = part
            formset.save()
            return redirect("part_list")
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
            "title": "Добавить деталь",
            "submit_label": "Создать",
        },
    )
