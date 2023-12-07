from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase

# Create your tests here.
from main.models import MRTLine, Station
from tests import FIXTURES_GROUP_ONLY


class InitializationTest(TransactionTestCase):
    """White box tests to check the implementation of the setup commands."""

    fixtures = FIXTURES_GROUP_ONLY

    def call_setup_command(self, command_name, *args, **kwargs):
        call_command(
            command_name,
            *args,
            stdout=StringIO(),
            stderr=StringIO(),
            **kwargs,
        )

    def test_load_stations(self):
        self.call_setup_command("update_train_stations", use_defaults=True)
        self.assertGreater(MRTLine.objects.count(), 0)
        self.assertGreater(Station.objects.count(), 0)
        self.assertGreater(MRTLine.objects.first().line_stations.count(), 0)
        self.assertGreater(Station.objects.first().train_line_stations.count(), 0)

    def test_create_lta_user(self):
        self.call_setup_command("create_lta_user", username="lta_test", password="lta_test")
        user = User.objects.get(username="lta_test")
        self.assertTrue(user.groups.filter(name="lta_users").exists())

    def test_update_lta_user(self):
        username = "test_user"
        user = User.objects.create_user(username=username, password="test_user")
        self.call_setup_command("add_user_to_lta", username=username)
        self.assertTrue(user.groups.filter(name="lta_users").exists())

