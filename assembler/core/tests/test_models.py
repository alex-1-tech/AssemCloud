from django.test import TestCase
from core.models import Machine, Assembly, Part


class MachineModelTest(TestCase):
    def test_str(self):
        machine = Machine.objects.create(name="Test Machine")
        self.assertEqual(str(machine), "Test Machine")


class AssemblyModelTest(TestCase):
    def test_str(self):
        machine = Machine.objects.create(name="Test Machine")
        assembly = Assembly.objects.create(name="Test Assembly", machine=machine)
        self.assertEqual(str(assembly), "Test Assembly")


class PartModelTest(TestCase):
    def test_str(self):
        machine = Machine.objects.create(name="Test Machine")
        assembly = Assembly.objects.create(name="Test Assembly", machine=machine)
        part = Part.objects.create(name="Test Part", assembly=assembly)
        self.assertEqual(str(part), "Test Part")
