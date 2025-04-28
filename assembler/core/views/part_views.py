from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from core.models import Part
from core.forms import PartForm
from django.db.models import Q


class PartListView(ListView):
    model = Part
    template_name = "core/parts/list.html"
    context_object_name = "parts"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        qs = Part.objects.select_related("assembly")
        return (
            qs.filter(
                Q(name__icontains=query) | Q(assembly__name__icontains=query)
            )
            if query
            else qs
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class PartCreateView(CreateView):
    model = Part
    form_class = PartForm
    template_name = "core/parts/add.html"
    success_url = reverse_lazy("list_parts")
