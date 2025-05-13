from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.forms import ManufacturerForm
from core.models.client import Manufacturer


class ManufacturerListView(ListView):
    model = Manufacturer
    template_name = "core/manufacturer/list.html"
    context_object_name = "manufacturers"

class ManufacturerCreateView(CreateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "core/manufacturer/edit.html"
    success_url = reverse_lazy("manufacturer_list")

class ManufacturerUpdateView(UpdateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "core/manufacturer/edit.html"
    success_url = reverse_lazy("manufacturer_list")

class ManufacturerDetailView(DetailView):
    model = Manufacturer
    template_name = "core/manufacturer/detail.html"
    context_object_name = "manufacturer"

class ManufacturerDeleteView(DeleteView):
    model = Manufacturer
    template_name = "core/manufacturer/confirm_delete.html"
    success_url = reverse_lazy("manufacturer_list")