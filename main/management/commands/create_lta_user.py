from getpass import getpass

from django.core.management import BaseCommand
from django.contrib.auth.models import Group, User

class Command(BaseCommand):
    help = "Creates a new LTA user."

    def add_arguments(self, parser):
        parser.add_argument('--username', required=False)
        parser.add_argument('--password', required=False)
        parser.add_argument('--email', required=False)

    def handle(self, *args, **options):
        if options["username"] and options["password"]:
            username = options["username"]
            password = options["password"]
            email = options["email"]
        else:
            self.stdout.write("Creating new user...")
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            password, password_confirm = "", ""

            while not password or password != password_confirm:
                password = getpass()
                password_confirm = getpass("Password (again): ")

        user = User.objects.create_user(username=username, password=password, email=email)
        lta_group, _created = Group.objects.get_or_create(name="lta_users")
        lta_group.user_set.add(user)

        self.stdout.write(
            self.style.SUCCESS("Done.")
        )