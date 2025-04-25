from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from core.models import Assembly
from core.forms import AssemblyForm
from django.db.models import Q

class AssemblyListView(ListView):
    model = Assembly
    template_name = 'core/list_assemblies.html'
    context_object_name = 'assemblies'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        qs = Assembly.objects.select_related('machine', 'parent_assembly')
        return qs.filter(Q(name__icontains=query) | Q(machine__name__icontains=query)) if query else qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class AssemblyCreateView(CreateView):
    model = Assembly
    form_class = AssemblyForm
    template_name = 'core/add_assembly.html'
    success_url = reverse_lazy('list_assemblies')
