from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Machine, Assembly, Part
from .forms import MachineForm, AssemblyForm, PartForm
import json

def list_machines(request):
    query = request.GET.get('q', '')
    machines = Machine.objects.filter(name__icontains=query) if query else Machine.objects.all()
    return render(request, 'core/list_machines.html', {'machines': machines, 'query': query})


def list_assemblies(request):
    query = request.GET.get('q', '')
    assemblies = Assembly.objects.select_related('machine', 'parent_assembly')
    if query:
        assemblies = assemblies.filter(
            Q(name__icontains=query) | Q(machine__name__icontains=query)
        )
    return render(request, 'core/list_assemblies.html', {'assemblies': assemblies, 'query': query})


def list_parts(request):
    query = request.GET.get('q', '')
    parts = Part.objects.select_related('assembly')
    if query:
        parts = parts.filter(
            Q(name__icontains=query) | Q(assembly__name__icontains=query)
        )
    return render(request, 'core/list_parts.html', {'parts': parts, 'query': query})


def add_machine(request):
    form = MachineForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('list_machines')
    return render(request, 'core/add_machine.html', {'form': form})


def add_assembly(request):
    form = AssemblyForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('list_assemblies')
    return render(request, 'core/add_assembly.html', {'form': form})


def add_part(request):
    form = PartForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('list_parts')
    return render(request, 'core/add_part.html', {'form': form})

@csrf_exempt
def save_all_objects(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        for m in data.get('machines', []):
            machine = Machine.objects.create(name=m['name'])
            for a in m.get('assemblies', []):
                assembly = Assembly.objects.create(name=a['name'], machine=machine)
                for p in a.get('parts', []):
                    Part.objects.create(name=p['name'], assembly=assembly)
        return JsonResponse({'status': 'success'})
