from django import forms
from core.models import Part


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'assembly']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'assembly': forms.Select(attrs={'class': 'form-control'}),
        }
