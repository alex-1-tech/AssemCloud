from django import forms
from .models import Machine, Assembly, Part


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AssemblyForm(forms.ModelForm):
    class Meta:
        model = Assembly
        fields = ['name', 'machine', 'parent_assembly']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'machine': forms.Select(attrs={'class': 'form-control'}),
            'parent_assembly': forms.Select(attrs={'class': 'form-control'}),
        }


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'assembly']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'assembly': forms.Select(attrs={'class': 'form-control'}),
        }
