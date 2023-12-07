from django.core.management import BaseCommand

from DataAPIManager.APILoader import APILoaderManager


class Command(BaseCommand):
    help = "Loads data from LTA API."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        manager = APILoaderManager()
        manager.scheduler_loop()

        self.stdout.write(
            self.style.SUCCESS("Done.")
        )
