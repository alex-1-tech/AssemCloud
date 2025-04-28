from django.test import TestCase
from django.urls import reverse
from core.models import Machine, Assembly, Part
from django.test import Client


class MachineListViewTest(TestCase):
    def setUp(self):
        self.machine = Machine.objects.create(name="Test Machine")

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/machines/")
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get("/machines/")
        self.assertTemplateUsed(response, "core/machines/list.html")

    def test_view_context_data(self):
        response = self.client.get("/machines/")
        self.assertIn("machines", response.context)


class MachineCreateViewTest(TestCase):
    def test_view_post_valid_data(self):
        response = self.client.post(reverse("add_machine"), {"name": "New Machine"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Machine.objects.count(), 1)

    def test_view_post_invalid_data(self):
        response = self.client.post(reverse("add_machine"), {"name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")


class AssemblyListViewTest(TestCase):
    def setUp(self):
        machine = Machine.objects.create(name="Test Machine")
        self.assembly = Assembly.objects.create(name="Test Assembly", machine=machine)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/assemblies/")
        self.assertEqual(response.status_code, 200)

    def test_view_context_data(self):
        response = self.client.get("/assemblies/")
        self.assertIn("assemblies", response.context)


class AssemblyCreateViewTest(TestCase):
    def test_view_post_valid_data(self):
        machine = Machine.objects.create(name="Test Machine")
        response = self.client.post(reverse("add_assembly"), {
            "name": "New Assembly",
            "machine": machine.id,
            "parent_assembly": ""
        })
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(Assembly.objects.count(), 1)

    def test_view_post_invalid_data(self):
        response = self.client.post(reverse("add_assembly"), {"name": "", "machine": ""})
        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, "This field is required.")


class PartListViewTest(TestCase):
    def setUp(self):
        machine = Machine.objects.create(name="Test Machine")
        assembly = Assembly.objects.create(name="Test Assembly", machine=machine)
        self.part = Part.objects.create(name="Test Part", assembly=assembly)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/parts/")
        self.assertEqual(response.status_code, 200)

    def test_view_context_data(self):
        response = self.client.get("/parts/")
        self.assertIn("parts", response.context)
