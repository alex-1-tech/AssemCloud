from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q

from core.models import Part
from core.forms import PartForm



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

class PartUpdateView(UpdateView):
    model = Part
    form_class = PartForm
    template_name = "core/parts/edit.html"
    context_object_name = "part"

    def get_success_url(self):
        return reverse_lazy("list_parts")

@method_decorator(csrf_exempt, name='dispatch')
class PartDeleteView(DeleteView):
    model = Part

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return super().post(request, *args, **kwargs)
