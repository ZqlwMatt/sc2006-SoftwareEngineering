from django.test import TestCase
from main.models import *
from django.test import TestCase, TransactionTestCase
import DataAPIManager.APILoader as APILoader
from DataAPIManager.db_API import dbAPI
from tests import FIXTURES
import datetime

class disruptionManager_test(TestCase):
    """
        Test users:
            - Registered user with preference set but wrong time
            - Registered user with preference set but correct time
            - Registered user with without preferences set
    """


    fixtures = FIXTURES


    def send_email(self, emaiL_list, disruptions, incidents):

        congestion_id={0:'Low', 1:'Moderately crowded', 2:'Very crowded', 999:'NA'}

        disrupted_stn = {}
        incident_stn_dict = {}
        if disruptions:
            disrupted_stn[174] = "Disruption"
        if incidents:
            incident_stn_dict[174] = "incident"

        stn = []
        for person in emaiL_list.keys():
            stn = []

            for data in emaiL_list[person]['stn_info']:
                if data[4] == 'everyday':
                    stn.append(
                        "\nCurrent congestion at {0} is: {1}\nCongestion predicted in 20mins time at {0} : {2}".format(
                            data[0], congestion_id[data[1]], congestion_id[data[2]]))

                if disruptions:
                    if data[3] in disrupted_stn.keys():
                        stn.append("\nALERT: {0}".format(disrupted_stn[data[3]]))
                if incidents:
                    if data[3] in incident_stn_dict.keys():
                        stn.append("\nIncident reported at {0}: \n{1}".format(data[0], incident_stn_dict[data[3]]))
            if not stn:
                continue

            email_body = "\n".join(stn)
        return stn

    def create_user(self,username, pw):
        user = User.objects.create(username=username)
        user.set_password(pw)
        user.save()

        return user

    def create_input(self, test_type):

        """
        Assumptions:
        Preferred station: 174
        Incident and Disruption Station: 174
        """

        # Set preference wrong_time
        if test_type == 1:
            return {1: {'email': "Hellow@email", 'stn_info': [["Stn 174", 0, 0, 174, 'disruption']]}}

        elif test_type == 2:
            return {1:{'email': "Hellow@email", 'stn_info' :[["Stn 201", 0, 0, 201, 'disruption']]}}

        elif test_type == 3:
            return {1:{'email': "Hellow@email", 'stn_info' :[["Stn 174", 0, 0, 174, 'everyday']]}}

        elif test_type == 4:
            return {}

    def test_1(self):

        # Insert preferences
        input_data = self.create_input(1)

        # Function
        res = self.send_email(input_data,0, 0)

        self.assertEqual(len(res),0)

    def test_2(self):

        # Insert preferences
        input_data = self.create_input(2)

        # Function
        res = self.send_email(input_data, 0, 1)

        self.assertEqual(len(res), 0)

    def test_3(self):
        #def send_email(self, emaiL_list, disruptions, incidents):
        # Insert preferences
        input_data = self.create_input(1)

        # Function
        res = self.send_email(input_data, 0, 1)

        self.assertEqual(len(res), 1)

    def test_4(self):
        #def send_email(self, emaiL_list, disruptions, incidents):
        # Insert preferences
        input_data = self.create_input(2)

        # Function
        res = self.send_email(input_data, 1, 0)

        self.assertEqual(len(res), 0)

    def test_5(self):
        #def send_email(self, emaiL_list, disruptions, incidents):
        # Insert preferences
        input_data = self.create_input(1)

        # Function
        res = self.send_email(input_data, 1, 0)
        self.assertEqual(len(res), 1)

    def test_6(self):
        #def send_email(self, emaiL_list, disruptions, incidents):
        # Insert preferences
        input_data = self.create_input(3)

        # Function
        res = self.send_email(input_data, 0, 0)

        self.assertEqual(len(res), 1)

    def test_7(self):
        #def send_email(self, emaiL_list, disruptions, incidents):
        # Insert preferences
        input_data = self.create_input(3)

        # Function
        res = self.send_email(input_data, 1, 1)

        self.assertEqual(len(res), 3)

    def test_8(self):
        #def send_email(self, emaiL_list, disruptions, incidents):
        # Insert preferences
        input_data = self.create_input(4)

        # Function
        res = self.send_email(input_data, 1, 1)

        self.assertEqual(len(res), 0)
