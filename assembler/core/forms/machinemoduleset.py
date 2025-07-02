"""Machine for configuring an inline formset between Module and MachineModule models.

This machine defines `MachineModuleFormSet`, an inline formset that allows managing
multiple `MachineModule` instances related to a single `Module` instance within the same
form. It is used primarily in views or admin interfaces where a user can create
or update a module along with its associated machine links in a single submission.
"""

from django.forms import inlineformset_factory

from core.forms import MachineModuleForm
from core.models import MachineModule, Module

MachineModuleFormSet = inlineformset_factory(
    parent_model=Module,
    model=MachineModule,
    form=MachineModuleForm,
    fk_name="module",
    extra=1,
    can_delete=True,
)
