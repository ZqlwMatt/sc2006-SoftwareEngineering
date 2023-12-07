from django.test import TestCase
from main.models import *
from django.test import TestCase, TransactionTestCase
import DataAPIManager.APILoader as APILoader
from DataAPIManager.db_API import dbAPI
from tests import FIXTURES
import datetime

class notifManager_test(TestCase):
    fixtures = FIXTURES
    def load_data(self, type):

        if type == "disruption":
            disruption_url = r"Test_files/TrainServiceAlerts/disruption.json"
        if type == "no_disruption":
            disruption_url = r"Test_files/TrainServiceAlerts/nodisruption.json"

        APILoader_obj = APILoader.APILoaderManager()
        disruption_data = APILoader_obj.pull_from_LTA_TEST_disruption(disruption_url)

        return disruption_data

    def test_disruption(self):

        disruption_data = self.load_data('disruption')['value']

        # ============== Function under test==============================
        if disruption_data['Status'] != 1:
            stn_data = disruption_data['AffectedSegments'][0]["Stations"].split(',')
            dbAPI.insert_majordisruption_db(dbAPI, created_at=disruption_data["Message"][0]["CreatedDate"],
                                            resolved_at=None,
                                            affected_stations=stn_data,
                                            description=disruption_data["Message"][0]["Content"])
        else:
            res = dbAPI.query_majordisruption_db(dbAPI)

            if res:
                dbAPI.insert_majordisruption_db(dbAPI, created_at=res[0].created_at,
                                                resolved_at=datetime.datetime.now(),
                                                affected_stations=None,
                                                description=res[0].description)
        # ============== /Function under test==============================
        self.assertTrue(MajorDisruption.objects.filter(resolved_at=None, created_at=disruption_data["Message"][0]["CreatedDate"]).exists())

    def test_no_disruption(self):
        disruption_data = self.load_data('no_disruption')['value']
        before_incident_added_count = MajorDisruption.objects.count()
        # ============== Function under test==============================
        if disruption_data['Status'] == 2:
            stn_data = disruption_data['AffectedSegments'][0]["Stations"].split(',')
            dbAPI.insert_majordisruption_db(dbAPI, created_at=disruption_data["Message"][0]["CreatedDate"],
                                            resolved_at=None,
                                            affected_stations=stn_data,
                                            description=disruption_data["Message"][0]["Content"])

        else:
            res = dbAPI.query_majordisruption_db(dbAPI)

            if res:
                dbAPI.insert_majordisruption_db(dbAPI, created_at=res[0].created_at,
                                                resolved_at=datetime.datetime.now(),
                                                affected_stations=None,
                                                description=res[0].description)
        # ============== /Function under test==============================
        self.assertEqual(MajorDisruption.objects.count(), before_incident_added_count)


    def test_disruption_resolved(self):
        # Insert data when disruption occurs
        disruption_data = self.load_data('disruption')['value']
        before_incident_added_count = MajorDisruption.objects.count()
        # ============== Function under test==============================
        if disruption_data['Status'] != 1:
            stn_data = disruption_data['AffectedSegments'][0]["Stations"].split(',')
            dbAPI.insert_majordisruption_db(dbAPI, created_at=disruption_data["Message"][0]["CreatedDate"],
                                            resolved_at=None,
                                            affected_stations=stn_data,
                                            description=disruption_data["Message"][0]["Content"])

        else:
            res = dbAPI.query_majordisruption_db(dbAPI)

            if res:
                dbAPI.insert_majordisruption_db(dbAPI, created_at=res[0].created_at,
                                                resolved_at=datetime.datetime.now(),
                                                affected_stations=None,
                                                description=res[0].description)
        # ============== /Function under test==============================

        # disruption resolved
        disruption_data = self.load_data('no_disruption')['value']

        # ============== Function under test==============================
        if disruption_data['Status'] != 1:
            stn_data = disruption_data['AffectedSegments'][0]["Stations"].split(',')
            dbAPI.insert_majordisruption_db(dbAPI, created_at=disruption_data["Message"][0]["CreatedDate"],
                                            resolved_at=None,
                                            affected_stations=stn_data,
                                            description=disruption_data["Message"][0]["Content"])
        else:
            res = dbAPI.query_majordisruption_db(dbAPI)

            if res:
                dbAPI.insert_majordisruption_db(dbAPI, created_at=res[0].created_at,
                                                resolved_at=datetime.datetime.now(),
                                                affected_stations=None,
                                                description=res[0].description)
        # ============== /Function under test==============================

        self.assertEqual(len(MajorDisruption.objects.filter(resolved_at__isnull=False)), before_incident_added_count+1)

