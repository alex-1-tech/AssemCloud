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

def create_assembly(data, machine, parent_assembly=None):
    name = data.get('name', '').strip()
    if not name:
        return

    assembly = Assembly.objects.create(
        name=name,
        machine=machine,
        parent_assembly=parent_assembly
    )

    for part in data.get('parts', []):
        part_name = part.get('name', '').strip()
        if part_name:
            Part.objects.create(name=part_name, assembly=assembly)

    for sub in data.get('sub_assemblies', []):
        create_assembly(sub, machine, assembly)


@csrf_exempt
def save_all_objects(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        machine_data = payload.get('machine')
        machine = Machine.objects.create(name=machine_data['name'])
        for assembly_data in machine_data.get('assemblies', []):
            create_assembly(assembly_data, machine)
        return JsonResponse({'status': 'success'})

def manage_objects_view(request):
    return render(request, 'core/manage_objects.html')