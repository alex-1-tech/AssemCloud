"""Module for configuring an inline formset between Part and ModulePart models.

This module defines `ModulePartFormSet`, an inline formset that allows managing
multiple `ModulePart` instances related to a single `Part` instance within the same
form. It is used primarily in views or admin interfaces where a user can create
or update a part along with its associated module links in a single submission.
"""
from django.forms import inlineformset_factory

from core.forms import ModulePartForm
from core.models import ModulePart, Part

ModulePartFormSet = inlineformset_factory(
    Part,
    ModulePart,
    form=ModulePartForm,
    extra=1,
    can_delete=True,
)
