from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import ManufacturerForm
from core.models import Manufacturer


class ManufacturerListView(ListView):
    model = Manufacturer
    template_name = "core/list.html"
    context_object_name = "manufacturers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            {
                "title": manufacturer.name,
                "subtitle": manufacturer.country,
                "view_url": reverse("manufacturer_detail", args=[manufacturer.pk]),
                "edit_url": reverse("manufacturer_edit", args=[manufacturer.pk]),
                "delete_url": reverse("manufacturer_delete", args=[manufacturer.pk]),
                "delete_confirm_message": f"Удалить {manufacturer.name}?",
            }
            for manufacturer in context["manufacturers"]
        ]

        context.update({
            "title": "Производители",
            "items": items,
            "add_url": reverse("manufacturer_add"),
            "add_label": "Добавить производителя",
            "empty_message": "Производители не найдены.",
        })
        return context


class ManufacturerCreateView(CreateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("manufacturer_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Добавить производителя",
            "submit_label": "Создать",
        })
        return context


class ManufacturerUpdateView(UpdateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "core/edit.html"
    success_url = reverse_lazy("manufacturer_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Редактировать производителя",
            "submit_label": "Сохранить",
        })
        return context


class ManufacturerDetailView(DetailView):
    model = Manufacturer
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manufacturer = self.object
        context.update({
            "title": "Производитель",
            "fields": [
                {"label": "Имя", "value": manufacturer.name},
                {"label": "Страна", "value": manufacturer.country},
                {"label": "Язык", "value": manufacturer.language},
                {"label": "Телефон", "value": manufacturer.phone},
            ],
            "edit_url": reverse("manufacturer_edit", args=[manufacturer.pk]),
            "delete_url": reverse("manufacturer_delete", args=[manufacturer.pk]),
        })
        return context


class ManufacturerDeleteView(DeleteView):
    model = Manufacturer
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("manufacturer_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manufacturer = self.object
        context.update({
            "title": "Удалить производителя",
            "message": f"Вы уверены, что хотите удалить производителя \
                {manufacturer.name}?",
            "confirm_label": "Удалить",
            "cancel_label": "Отмена",
            "cancel_url": reverse("manufacturer_detail", args=[manufacturer.pk]),
        })
        return context
