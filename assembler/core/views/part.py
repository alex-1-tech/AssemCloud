"""Views for managing parts.

Includes listing, creating, updating, viewing, and deleting parts.
"""
from typing import Any

from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import ModulePartForm, PartForm
from core.mixins import NextUrlMixin, QuerySetMixin
from core.models import ModulePart, Part

PART_LIST_URL = "part_list"

class PartListView(QuerySetMixin, ListView):
    """Displays a list of all parts."""

    model = Part
    template_name = "core/list.html"
    context_object_name = "items"
    paginate_by = 7

    def get_context_data(self, **kwargs: object) -> dict:
        """Add context metadata and card items for listing parts."""
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "title": "Детали",
                "items": self.get_part_items(context["items"]),
                "add_url": reverse("part_add"),
                "empty_message": "Детали не найдены.",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context

    def get_part_items(
        self, parts: list[Part],
        ) -> list[dict[str, Any]]:
        """Generate a list of dictionary items.

        Representing part metadata for UI rendering.
        """
        return [
            {
                "title": part.name,
                "subtitle": (
                    "Производитель: "
                    f"{part.manufacturer.name if part.manufacturer else 'не указан'}"
                ),
                "view_url": reverse("part_detail", args=[part.pk]),
                "edit_url": reverse(
                    "part_edit", args=[part.pk],
                    ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("part_delete", args=[part.pk]),
                "delete_confirm_message": f"Удалить деталь {part.name}?",
            }
            for part in parts
        ]


    def get_queryset(self) -> object:
        """Return a queryset of blueprints filtered by the search query."""
        q = self.request.GET.get("q", "").strip()
        return self.get_queryset_default(
            q,
            Q(Q(name__icontains=q) | Q(manufacturer__name__icontains=q)),
        )


class PartCreateView(NextUrlMixin, CreateView):
    """Handles creation of a new part."""

    model = Part
    form_class = PartForm
    template_name = "core/parts/edit.html"
    default_redirect_url_name = PART_LIST_URL

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
            "request": self.request,
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



class PartUpdateView(NextUrlMixin, UpdateView):
    """Handles editing an existing part."""

    model = Part
    form_class = PartForm
    template_name = "core/parts/edit.html"
    default_redirect_url_name = PART_LIST_URL

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
            "request": self.request,
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

    def get_part_fields(
        self, part: Part,
        ) -> list[dict[str, Any]]:
        """Construct a list of field metadata.

        For displaying part attributes in the UI.
        """
        return [
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
        ]

    def get_context_data(self, **kwargs: object) -> dict:
        """Add part fields and actions to context."""
        context = super().get_context_data(**kwargs)
        part = self.object
        context.update(
            {
                "title": "Деталь",
                "subtitle": part.name,
                "fields": self.get_part_fields(part),
                "add_url": reverse("part_add"),
                "edit_url": reverse(
                    "part_edit", args=[part.pk],
                ) + f"?next={self.request.get_full_path()}",
                "delete_url": reverse("part_delete", args=[part.pk]),
                "add_label": "Добавить новую деталь",
                "user_roles": list(
                    self.request.user.roles.values_list("role__name", flat=True),
                ),
            },
        )
        return context


class PartDeleteView(NextUrlMixin, DeleteView):
    """Handles deletion confirmation for a part."""

    model = Part
    template_name = "core/confirm_delete.html"
    default_redirect_url_name = PART_LIST_URL

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
