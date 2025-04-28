from django.test import TestCase
from core.forms import MachineForm, AssemblyForm, PartForm
from core.models import Machine, Assembly


class MachineFormTest(TestCase):
    def test_valid_form(self):
        form_data = {"name": "Test Machine"}
        form = MachineForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {"name": ""}
        form = MachineForm(data=form_data)
        self.assertFalse(form.is_valid())


class AssemblyFormTest(TestCase):
    def test_valid_form(self):
        machine = Machine.objects.create(name="Test Machine")
        form_data = {"name": "Test Assembly", "machine": machine.id, "parent_assembly": ""}
        form = AssemblyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {"name": "", "machine": "", "parent_assembly": ""}
        form = AssemblyForm(data=form_data)
        self.assertFalse(form.is_valid())


class PartFormTest(TestCase):
    def test_valid_form(self):
        machine = Machine.objects.create(name="Test Machine")
        assembly = Assembly.objects.create(name="Test Assembly", machine=machine)
        form_data = {"name": "Test Part", "assembly": assembly.id}
        form = PartForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {"name": "", "assembly": ""}
        form = PartForm(data=form_data)
        self.assertFalse(form.is_valid())
