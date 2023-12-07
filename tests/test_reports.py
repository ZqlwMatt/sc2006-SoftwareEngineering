from datetime import timedelta

from django.conf import settings
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY, get_user_model, authenticate
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

# Create your tests here.
from main.models import  Incident, IncidentReport
from tests import FIXTURES

TEST_PASSWORD = "IHateCongestionNation123*"
INVALID_SHIFT = timedelta(hours=Incident.TIME_THRESHOLD, minutes=1)  # 24h 1m between first and last report
VALID_SHIFT = timedelta(hours=Incident.TIME_THRESHOLD) - timedelta(minutes=1)  # 23h 59m between first and last report
PRIMARY_STATION = "Boon Lay"
SECONDARY_STATION = "Pioneer"

class IncidentReportTest(StaticLiveServerTestCase):
    """Black box tests to check the creation of incidents when the incident report form is submitted."""

    fixtures = FIXTURES

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_user_must_be_logged_in(self):
        response = self.client.get("/forms/report-incident/", follow=True)
        self.assertRedirects(response, "/login/?next=/forms/report-incident/")

    def get_session_cookie(self, user):
        user = authenticate(
            username=user.username,
            password=TEST_PASSWORD,
        )
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()

        cookie = {
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'secure': False,
            'path': '/',
        }

        return cookie

    def report_incident(self, user, station_name, shift_back=None):
        self.client.login(username=user.username, password=TEST_PASSWORD)  # Native django test client

        cookie = self.get_session_cookie(user)

        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie(cookie)
        self.selenium.refresh()  # need to update page for logged in user

        self.selenium.get(f"{self.live_server_url}/forms/report-incident/")
        self.assertEqual(
            self.selenium.current_url,
            f"{self.live_server_url}/forms/report-incident/"
        )  # make sure login is ok

        # click on the station input field
        self.selenium.find_element(By.CSS_SELECTOR, ".select2-selection").click()
        self.selenium.find_element(By.CSS_SELECTOR, ".select2-search__field").click()

        # search for Boon Lay
        self.selenium.find_element(By.CSS_SELECTOR, ".select2-search__field").send_keys(station_name.lower())

        # wait for results to load
        self.selenium.implicitly_wait(5)

        # click on first result
        self.selenium.find_element(By.CSS_SELECTOR,
                                   ".select2-results__option.select2-results__option--highlighted").click()

        # click on description field and enter some sample text
        self.selenium.find_element(By.ID, "id_description").click()
        self.selenium.find_element(By.ID, "id_description").send_keys("test")

        # click outside the description field
        self.selenium.find_element(By.CSS_SELECTOR, "html").click()

        # click submit
        self.selenium.find_element(By.ID, "submit-id-submit").click()

        # wait for next page to load, ensure form submitted properly
        self.selenium.implicitly_wait(5)
        
        if shift_back is not None:
            report = IncidentReport.objects.latest("reported_at")  # access the latest report
            report.reported_at = report.reported_at - shift_back  # pull the reported timing back to test the boundary case
            report.save()
            

    def test_all_valid_incident_created(self):
        initial_incidents = Incident.objects.count()
        initial_reports = IncidentReport.objects.count()
        n = 0

        for user in get_user_model().objects.all():
            if n == 0:
                self.report_incident(user, PRIMARY_STATION, shift_back=VALID_SHIFT)
            else:
                self.report_incident(user, PRIMARY_STATION)
            n += 1

        final_incidents = Incident.objects.count()
        final_reports = IncidentReport.objects.count()

        self.assertEqual(final_reports - initial_reports, 5)  # 5 incident reports created
        self.assertEqual(final_incidents - initial_incidents, 1)  # 1 incident created

    def test_4_reports_incident_not_created(self):
        initial_incidents = Incident.objects.count()
        initial_reports = IncidentReport.objects.count()
        n = 0

        for user in get_user_model().objects.all():
            if n == 0:
                self.report_incident(user, PRIMARY_STATION, shift_back=VALID_SHIFT)
            elif n >= 4:
                break
            else:
                self.report_incident(user, PRIMARY_STATION)
            n += 1

        final_incidents = Incident.objects.count()
        final_reports = IncidentReport.objects.count()

        self.assertEqual(final_reports - initial_reports, 4)  # 4 incident reports created
        self.assertEqual(final_incidents - initial_incidents, 0)  # no incident created

    def test_4_distinct_users_incident_not_created(self):
        initial_incidents = Incident.objects.count()
        initial_reports = IncidentReport.objects.count()
        users = get_user_model().objects.all()
        n = 0

        for user in users:
            if n == 0:
                self.report_incident(user, PRIMARY_STATION, shift_back=VALID_SHIFT)
            else:
                if n >= 4:
                    user = users[0]  # use the first user again so we only have 4 distinct users
                self.report_incident(user, PRIMARY_STATION)
            n += 1

        final_incidents = Incident.objects.count()
        final_reports = IncidentReport.objects.count()

        self.assertEqual(final_reports - initial_reports, 5)  # 5 incident reports created
        self.assertEqual(final_incidents - initial_incidents, 0)  # no incident created

    def test_different_stations_incident_not_created(self):
        initial_incidents = Incident.objects.count()
        initial_reports = IncidentReport.objects.count()
        n = 0

        for user in get_user_model().objects.all():
            if n == 0:
                self.report_incident(user, PRIMARY_STATION, shift_back=VALID_SHIFT)
            elif n >= 4:
                self.report_incident(user, SECONDARY_STATION)  # use a different station
            else:
                self.report_incident(user, PRIMARY_STATION)
            n += 1

        final_incidents = Incident.objects.count()
        final_reports = IncidentReport.objects.count()

        self.assertEqual(final_reports - initial_reports, 5)  # 5 incident reports created
        self.assertEqual(final_incidents - initial_incidents, 0)  # no incident created

    def test_interval_long_incident_not_created(self):
        initial_incidents = Incident.objects.count()
        initial_reports = IncidentReport.objects.count()
        n = 0

        for user in get_user_model().objects.all():
            if n == 0:
                self.report_incident(user, PRIMARY_STATION, shift_back=INVALID_SHIFT)
            else:
                self.report_incident(user, PRIMARY_STATION)
            n += 1

        final_incidents = Incident.objects.count()
        final_reports = IncidentReport.objects.count()

        self.assertEqual(final_reports - initial_reports, 5)  # 5 incident reports created
        self.assertEqual(final_incidents - initial_incidents, 0)  # no incident created
