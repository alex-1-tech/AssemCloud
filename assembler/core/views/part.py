"""Views for managing parts.

Includes listing, creating, updating, viewing, and deleting parts.
"""

from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import ModulePartForm, PartForm
from core.models import ModulePart, Part


class PartListView(ListView):
    """Displays a list of all parts."""

    model = Part
    template_name = "core/list.html"
    context_object_name = "items"
    paginate_by = 10

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata and card items for listing parts."""
        context = super().get_context_data(**kwargs)
        parts = context["items"]

        items = [
            {
                "title": part.name,
                "subtitle": (
                    "Производитель: "
                    f"{part.manufacturer.name if part.manufacturer else 'не указан'}"
                ),
                "view_url": reverse("part_detail", args=[part.pk]),
                "edit_url": reverse("part_edit", args=[part.pk]),
                "delete_url": reverse("part_delete", args=[part.pk]),
                "delete_confirm_message": f"Удалить деталь {part.name}?",
            }
            for part in parts
        ]

        context.update(
            {
                "title": "Детали",
                "items": items,
                "add_url": reverse("part_add"),
                "add_label": "Добавить деталь",
                "empty_message": "Детали не найдены.",
            },
        )
        return context

    def get_queryset(self) -> object:
        """Return a queryset of parts filtered by the search query."""
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(manufacturer__name__icontains=q),
            )
        return qs


class PartCreateView(CreateView):
    """Handles creation of a new part."""

    model = Part
    form_class = PartForm
    template_name = "core/parts/edit.html"
    success_url = reverse_lazy("part_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata and formset for creating a part."""
        context = super().get_context_data(**kwargs)
        module_id = self.request.GET.get("module")

        module_part_formset = inlineformset_factory(
            Part, ModulePart,
            form=ModulePartForm,
            extra=1 if module_id else 0,
            can_delete=True,
        )

        if self.request.POST:
            context["formset"] = module_part_formset(self.request.POST)
        else:
            context["formset"] = module_part_formset(queryset=ModulePart.objects.none())
            if module_id:
                context["formset"].forms[0].initial["module"] = module_id
                context["module_id"] = module_id

        context.update({
            "title": "Добавить деталь",
            "submit_label": "Создать",
        })

        return context

    def form_valid(self, form: PartForm) -> object:
        """Validate form and related formset, then save."""
        context = self.get_context_data()
        formset: BaseInlineFormSet = context["formset"]
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        return self.form_invalid(form)



class PartUpdateView(UpdateView):
    """Handles editing an existing part."""

    model = Part
    form_class = PartForm
    template_name = "core/parts/edit.html"
    success_url = reverse_lazy("part_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata and formset for editing a part."""
        context = super().get_context_data(**kwargs)
        module_id = self.request.GET.get("module")

        module_part_formset = inlineformset_factory(
            Part,
            ModulePart,
            form=ModulePartForm,
            extra=1 if module_id else 0,
            can_delete=True,
        )

        if self.request.POST:
            context["formset"] = module_part_formset(
                self.request.POST, instance=self.object,
            )
        else:
            context["formset"] = module_part_formset(instance=self.object)
            if module_id:
                context["module_id"] = module_id

        context.update({
            "title": "Редактировать деталь",
            "submit_label": "Сохранить",
        })
        return context

    def form_valid(self, form: PartForm) -> object:
        """Validate form and related formset, then save."""
        context = self.get_context_data()
        formset: BaseInlineFormSet = context["formset"]
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        return self.form_invalid(form)


class PartDetailView(DetailView):
    """Displays detailed information about a part."""

    model = Part
    template_name = "core/detail.html"

    def get_context_data(self, **kwargs: object) -> dict:
        """Add part fields and actions to context."""
        context = super().get_context_data(**kwargs)
        part = self.object
        context.update(
            {
                "title": "Деталь",
                "fields": [
                    {"label": "Название", "value": part.name},
                    {"label": "Описание", "value": part.description or "Нет описания"},
                    {"label": "Материал", "value": part.material or "Не указан"},
                    {
                        "label": "Дата производства",
                        "value": part.manufacture_date or "Не указана",
                    },
                    {
                        "label": "Модули",
                        "value": [
                            {
                                "name": mp.module.name,
                                "url": reverse("module_detail", args=[mp.module.pk]),
                                "quantity": mp.quantity,
                            }
                            for mp in part.part_modules.select_related("module")
                        ],
                        "is_links": True,
                    },
                ],
                "add_url": reverse("part_add"),
                "edit_url": reverse("part_edit", args=[part.pk]),
                "delete_url": reverse("part_delete", args=[part.pk]),
                "add_label": "Добавить новую деталь",

            },
        )
        return context


class PartDeleteView(DeleteView):
    """Handles deletion confirmation for a part."""

    model = Part
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("part_list")

    def get_context_data(self, **kwargs: object) -> dict:
        """Add confirmation message and actions to context."""
        context = super().get_context_data(**kwargs)
        part = self.object
        context.update(
            {
                "title": "Удалить деталь",
                "message": f"Вы уверены, что хотите удалить деталь {part.name}?",
                "confirm_label": "Удалить",
                "cancel_label": "Отмена",
                "cancel_url": reverse("part_detail", args=[part.pk]),
            },
        )
        return context
