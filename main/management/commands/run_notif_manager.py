from django.core.management import BaseCommand

from notifManager.notifManager import NotifManager


class Command(BaseCommand):
    help = "Sends the required notifications."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        manager = NotifManager()
        manager.scheduler_loop()

        self.stdout.write(
            self.style.SUCCESS("Done.")
        )
