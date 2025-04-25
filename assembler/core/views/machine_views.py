from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from core.models import Machine
from core.forms import MachineForm

class MachineListView(ListView):
    model = Machine
    template_name = 'core/machines/list.html'
    context_object_name = 'machines'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Machine.objects.filter(name__icontains=query) if query else Machine.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class MachineCreateView(CreateView):
    model = Machine
    form_class = MachineForm
    template_name = 'core/machines/add.html'
    success_url = reverse_lazy('list_machines')
