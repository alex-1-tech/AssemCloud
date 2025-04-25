from django import forms
from core.models import Machine


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
