from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import ModuleForm  # Предполагается, что форма создана
from core.models import Module
from core.services.assembly_tree import build_module_tree


class ModuleListView(ListView):
    model = Module
    template_name = "core/list.html"
    context_object_name = "modules"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": module.name,
                "subtitle": "s/n: " + module.serial,
                "view_url": reverse("module_detail", args=[module.pk]),
                "edit_url": reverse("module_edit", args=[module.pk]),
                "delete_url": reverse("module_delete", args=[module.pk]),
                "delete_confirm_message": f"Удалить модуль {module.name}?",
            }
            for module in context["modules"]
        ]
        context.update({
            "title": "Модули",
            "items": items,
            "add_url": reverse("module_add"),
            "add_label": "Добавить модуль",
            "empty_message": "Модули не найдены.",
        })
        return context


class ModuleCreateView(CreateView):
    model = Module
    form_class = ModuleForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("module_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Добавить модуль",
            "submit_label": "Создать",
        })
        return context


class ModuleUpdateView(UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("module_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Редактировать модуль",
            "submit_label": "Сохранить",
        })
        return context


class ModuleDetailView(DetailView):
    model = Module
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs):
        module = self.object
        module_tree = build_module_tree(module)
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Модуль",
            "fields": [
                {"label": "Машина", "value": module.machine},
                {"label": "Название модуля", "value": module.name},
                {"label": "Артикул", "value": module.part_number},
                {"label": "Серийный номер", "value": module.serial},
                {"label": "Версия", "value": module.version},
                {"label": "Статус", "value": module.get_module_status_display()},
                {
                    "label": "Чертёж", 
                    "value": module.blueprint if module.blueprint else "Нет чертежа"
                },
                {
                    "label": "Родительский модуль", 
                    "value": module.parent if module.parent else "Нет родителя"
                },
            ],
            "module_tree": module_tree,
            "edit_url": reverse("module_edit", args=[module.pk]),
            "delete_url": reverse("module_delete", args=[module.pk]),
        })
        return context


class ModuleDeleteView(DeleteView):
    model = Module
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("module_list")

    def get_context_data(self, **kwargs):
        module = self.object
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Удалить модуль",
            "message": f"Вы уверены, что хотите удалить модуль {module.name}?",
            "confirm_label": "Удалить",
            "cancel_label": "Отмена",
            "cancel_url": reverse("module_detail", args=[module.pk]),
        })
        return context
