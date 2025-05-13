from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import BlueprintForm
from core.models import Blueprint


class BlueprintListView(ListView):
    model = Blueprint
    template_name = "core/list.html"
    context_object_name = "blueprints"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": str(bp),
                "subtitle": (
                    f"Производитель: \
                        {bp.manufacturer}" if bp.manufacturer else "Без производителя",
                ),
                "view_url": reverse("blueprint_detail", args=[bp.pk]),
                "edit_url": reverse("blueprint_edit", args=[bp.pk]),
                "delete_url": reverse("blueprint_delete", args=[bp.pk]),
                "delete_confirm_message": f"Удалить чертеж {bp}?",
            }
            for bp in context["blueprints"]
        ]
        context.update({
            "title": "Чертежи",
            "items": items,
            "add_url": reverse("blueprint_add"),
            "add_label": "Добавить чертеж",
            "empty_message": "Чертежи не найдены.",
        })
        return context


class BlueprintCreateView(CreateView):
    model = Blueprint
    form_class = BlueprintForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("blueprint_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Добавить чертеж",
            "submit_label": "Создать",
        })
        return context


class BlueprintUpdateView(UpdateView):
    model = Blueprint
    form_class = BlueprintForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("blueprint_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Редактировать чертеж",
            "submit_label": "Сохранить",
        })
        return context


class BlueprintDetailView(DetailView):
    model = Blueprint
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs):
        bp = self.object
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Чертеж",
            "fields": [
                {"label": "Вес", "value": bp.weight},
                {"label": "Масштаб", "value": bp.scale},
                {"label": "Версия", "value": bp.version},
                {"label": "Схема наименования", "value": bp.naming_scheme},
                {"label": "Разработчик", "value": bp.developer},
                {"label": "Проверяющий", "value": bp.validator},
                {"label": "Главный конструктор", "value": bp.chief_designer},
                {
                    "label": "Файл (PDF)", 
                    "value": bp.scheme_file.url if bp.scheme_file else None
                },
                {
                    "label": "Файл (STEP)", 
                    "value": bp.step_file.url if bp.step_file else None
                },
            ],
            "edit_url": reverse("blueprint_edit", args=[bp.pk]),
            "delete_url": reverse("blueprint_delete", args=[bp.pk]),
        })
        return context


class BlueprintDeleteView(DeleteView):
    model = Blueprint
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("blueprint_list")

    def get_context_data(self, **kwargs):
        bp = self.object
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Удалить чертеж",
            "message": f"Вы уверены, что хотите удалить чертеж {bp}?",
            "confirm_label": "Удалить",
            "cancel_label": "Отмена",
            "cancel_url": reverse("blueprint_detail", args=[bp.pk]),
        })
        return context
