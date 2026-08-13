from django.core.management.base import BaseCommand

from core.schemes import sync_models_and_schemes


class Command(BaseCommand):
    help = "Loads default equipment dynamic schemes into the database"

    def handle(self, *args: object, **options: object) -> None:
        sync_models_and_schemes()
        self.stdout.write(self.style.SUCCESS("Schemes successfully loaded."))
