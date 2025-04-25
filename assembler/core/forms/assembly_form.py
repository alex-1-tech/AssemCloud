from django import forms
from core.models import Assembly

class AssemblyForm(forms.ModelForm):
    class Meta:
        model = Assembly
        fields = ['name', 'machine', 'parent_assembly']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'machine': forms.Select(attrs={'class': 'form-control'}),
            'parent_assembly': forms.Select(attrs={'class': 'form-control'}),
        }
