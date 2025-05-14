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
                "title": str(bp.naming_scheme) + ' - ' + str(bp.version),
                "subtitle": (
                    f"Производитель: \
                        {bp.manufacturer}" if bp.manufacturer else "Без производителя"
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
    template_name = "core/blueprints/edit.html"
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
    template_name = "core/blueprints/detail.html"

    def get_context_data(self, **kwargs):
        bp = self.object
        request = self.request
        context = super().get_context_data(**kwargs)

        # Ссылки на файлы чертежей
        scheme_url = request.build_absolute_uri(bp.scheme_file.url) \
            if bp.scheme_file else None
        step_url = request.build_absolute_uri(bp.step_file.url) \
            if bp.step_file else None

        # Ссылки на профили пользователей
        developer_url = reverse("user_profile", args=[bp.developer.pk]) \
            if bp.developer else None
        validator_url = reverse("user_profile", args=[bp.validator.pk]) \
            if bp.validator else None
        lead_designer_url = reverse("user_profile", args=[bp.lead_designer.pk]) \
            if bp.lead_designer else None
        chief_designer_url = reverse("user_profile", args=[bp.chief_designer.pk]) \
            if bp.chief_designer else None
        approver_url = reverse("user_profile", args=[bp.approver.pk]) \
            if bp.approver else None


        context.update({
            "title": "Чертеж",
                    "scheme_url": scheme_url,
        "step_url": step_url,
            "fields": [
                {"label": "Вес", "value": bp.weight},
                {"label": "Масштаб", "value": bp.scale},
                {"label": "Версия", "value": bp.version},
                {"label": "Схема наименования", "value": bp.naming_scheme},
                {
                    "label": "Разработчик", "value": bp.developer, 
                    "profile_url": developer_url
                },
                {
                    "label": "Проверяющий", "value": bp.validator, 
                    "profile_url": validator_url
                },
                {
                    "label": "Ведущий конструктор", "value": bp.lead_designer, 
                    "profile_url": lead_designer_url
                },
                {
                    "label": "Главный конструктор", "value": bp.chief_designer, 
                    "profile_url": chief_designer_url
                },
                {
                    "label": "Утвердивший", "value": bp.approver, 
                    "profile_url": approver_url
                },
                {"label": "Производитель", "value": bp.manufacturer},
                {
                    "label": "Файл (PDF)", 
                    "value": scheme_url
                },
                {
                    "label": "Файл (STEP)", 
                    "value": step_url
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
