from django.test import TestCase
from core.services.save_machine import save_machine
from core.models import Machine, Assembly, Part


class SaveMachineTest(TestCase):
    def test_save_machine_with_assemblies_and_parts(self):
        machine_data = {
            "name": "Test Machine",
            "assemblies": [
                {
                    "name": "Test Assembly",
                    "parts": [{"name": "Part 1"}, {"name": "Part 2"}],
                    "sub_assemblies": []
                }
            ]
        }

        machine = save_machine(machine_data)
        self.assertEqual(Machine.objects.count(), 1)
        self.assertEqual(Assembly.objects.count(), 1)
        self.assertEqual(Part.objects.count(), 2)
        self.assertEqual(machine.name, "Test Machine")
