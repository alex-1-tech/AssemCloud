from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View

from core.models import Machine
from core.services.parse_machine import parse_machine

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class MachineImportSelectView(View):
    """Страница выбора машины и файла для импорта."""

    template_name = "core/machines/import_select.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        machines = Machine.objects.all()
        return render(request, self.template_name, {"machines": machines})


class MachineImportProcessView(View):
    """Принимает POST с выбором машины и XLSX, парсит и привязывает данные."""

    def post(self, request: HttpRequest) -> HttpResponse:
        machine_id = request.POST.get("machine")
        xlsx_file = request.FILES.get("xlsx_file")

        if not machine_id or not xlsx_file:
            messages.error(request, "Нужно выбрать машину и файл.")
            return redirect(reverse_lazy("machine_import_select"))

        machine = get_object_or_404(Machine, pk=machine_id)

        try:
            result = parse_machine(xlsx_file, machine)
            messages.success(
                request,
                f"Импорт завершён: создано {result['modules_created']} модулей, "
                f"обновлено {result['links_created_or_updated']} связей.",
            )
        except Exception as exc:
            logger.exception("Ошибка импорта XLSX файла")
            messages.error(request, f"Ошибка при разборе файла: {exc}")

        return redirect(reverse_lazy("machine_list"))
