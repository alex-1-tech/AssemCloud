from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from core.models import Machine, Assembly, Part
from core.forms import MachineForm
from django.db.models import Prefetch

def recursive_assembly_prefetch():
    return Prefetch(
        'sub_assemblies',
        queryset=Assembly.objects.all().prefetch_related(
            'part_set',
            Prefetch('sub_assemblies', queryset=Assembly.objects.all().prefetch_related('part_set'))
        ),
        to_attr='prefetched_sub_assemblies'
    )

class MachineListView(ListView):
    model = Machine
    template_name = "core/machines/list.html"
    context_object_name = "machines"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        qs = Machine.objects.all()
        if query:
            qs = qs.filter(name__icontains=query)

        return qs.prefetch_related(
            Prefetch(
                'assembly_set',
                queryset=Assembly.objects.filter(parent_assembly__isnull=True).prefetch_related(
                    'part_set',
                    recursive_assembly_prefetch()
                ),
                to_attr='root_assemblies'
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class MachineCreateView(CreateView):
    model = Machine
    form_class = MachineForm
    template_name = "core/machines/add.html"
    success_url = reverse_lazy("list_machines")
