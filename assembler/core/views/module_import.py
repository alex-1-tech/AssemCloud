from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from core.models import Module
from core.services.parse_machine import parse_module


class ModuleImportSelectView(View):
    """
    View to select a parent module and upload an XLSX file for import.

    Renders a form with a list of existing modules and a file upload input.
    """

    template_name = "core/modules/import_select.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        modules = Module.objects.all()
        return render(request, self.template_name, {"modules": modules})


class ModuleImportProcessView(View):
    """
    Handles POST with a selected parent module and uploaded XLSX file.

    Parses the file and attaches parts or submodules to the selected module.
    """

    def post(self, request: HttpRequest) -> HttpResponse:
        module_id = request.POST.get("module")
        xlsx_file = request.FILES.get("xlsx_file")

        if not module_id or not xlsx_file:
            messages.error(request, "You must select a module and upload a file.")
            return redirect(reverse_lazy("module_import_select"))

        try:
            parent_module = Module.objects.get(pk=module_id)
            result = parse_module(xlsx_file, parent_module)
            messages.success(
                request,
                f"Imported into module “{parent_module.name}”: "
                f"{result['modules_created']} created, {result['links_created_or_updated']} linked.",
            )
        except Module.DoesNotExist:
            messages.error(request, "Selected module was not found.")
        except Exception as exc:
            messages.error(request, f"Error while parsing XLSX: {exc}")

        return redirect(reverse_lazy("module_list"))
