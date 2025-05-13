from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import PartForm
from core.models import Part


class PartListView(ListView):
    model = Part
    template_name = "core/list.html"
    context_object_name = "parts"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": part.name,
                "subtitle": part.manufacturer.name if part.manufacturer else "",
                "view_url": reverse("part_detail", args=[part.pk]),
                "edit_url": reverse("part_edit", args=[part.pk]),
                "delete_url": reverse("part_delete", args=[part.pk]),
                "delete_confirm_message": f"Удалить {part.name}?",
            }
            for part in context["parts"]
        ]

        context.update({
            "title": "Детали",
            "items": items,
            "add_url": reverse("part_add"),
            "add_label": "Добавить деталь",
            "empty_message": "Детали не найдены.",
        })
        return context


class PartCreateView(CreateView):
    model = Part
    form_class = PartForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("part_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Добавить деталь",
            "submit_label": "Создать",
        })
        return context


class PartUpdateView(UpdateView):
    model = Part
    form_class = PartForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("part_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Редактировать деталь",
            "submit_label": "Сохранить",
        })
        return context


class PartDetailView(DetailView):
    model = Part
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        part = self.object
        context.update({
            "title": "Деталь",
            "fields": [
                {"label": "Название", "value": part.name},
                {
                    "label": "Производитель", 
                    "value": part.manufacturer.name if part.manufacturer else "—"
                },
                {"label": "Описание", "value": part.description},
                {"label": "Материал", "value": part.material},
                {"label": "Дата производства", "value": part.manufacture_date},
            ],
            "edit_url": reverse("part_edit", args=[part.pk]),
            "delete_url": reverse("part_delete", args=[part.pk]),
        })
        return context


class PartDeleteView(DeleteView):
    model = Part
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("part_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        part = self.object
        context.update({
            "title": "Удалить деталь",
            "message": f"Вы уверены, что хотите удалить деталь \
                {part.name}?",
            "confirm_label": "Удалить",
            "cancel_label": "Отмена",
            "cancel_url": reverse("part_detail", args=[part.pk]),
        })
        return context
