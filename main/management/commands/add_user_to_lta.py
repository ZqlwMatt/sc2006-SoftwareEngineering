from getpass import getpass

from django.core.management import BaseCommand
from django.contrib.auth.models import Group, User


class Command(BaseCommand):
    help = "Creates a new LTA user."

    def add_arguments(self, parser):
        parser.add_argument('--username', required=False)

    def handle(self, *args, **options):
        if options["username"]:
            username = options["username"]
        else:
            self.stdout.write("Updating existing user to LTA user...")
            username = input("Username: ").strip()

        try:
            user = User.objects.get(username=username)
            lta_group, _created = Group.objects.get_or_create(name="lta_users")
            lta_group.user_set.add(user)
            self.stdout.write(
                self.style.SUCCESS("Done.")
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Specified user does not exist.")
            )
