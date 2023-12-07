import json
import requests
from DataAPIManager.db_API import dbAPI
import datetime
from django.utils import timezone

class APILoaderManager():
    """
    Function of this class is to:
    1) Pull data from LTA API
    2) Push data into db
    3) Schedules to run every 10mins
    """
    def __init__(self):

        # self.get_auth_headers = {'accept': 'application/json',
        #                      "AccountKey": "qfmORDTTRTSy8qiKeNAzkg=="}
        self.get_auth_headers = {'accept': 'application/json',
                                 "AccountKey": "tFsLDEipS2qEwrWL6Vj7Yw=="}

        self.forecast_url = "http://datamall2.mytransport.sg/ltaodataservice/PCDForecast"
        self.realtime_url = "http://datamall2.mytransport.sg/ltaodataservice/PCDRealTime"
        self.disruption_url = "http://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"

        self.time_scheduler = 10
        self.db_obj= dbAPI()

        #self.train_line = ['NSL']
        self.train_line = ['CCL', 'CEL', 'CGL', 'DTL', 'EWL', 'NEL', 'NSL', 'BPL', 'SLRT', 'PLRT']
        self.crowdlevel_dict = {'l':0, 'm':1, 'h':2, 'na':999}

    def pull_from_LTA(self, url, params=None):
        if params is None:
            params = dict()

        response = requests.get(url, headers=self.get_auth_headers, params=params)
        print("DATA PULLED FROM LTAMALL", response.text)
        return response.json()

    def pull_from_LTA_TEST(self, URL=0, line="NSL"):
        file = rf"C:\Users\Creaton\PycharmProjects\2006_sanity\Test_files\realtime\{line}.json"
        with open(file) as f:
            data = json.load(f)

        return data

    def pull_from_LTA_TEST_disruption(self, URL=r"Test_files/TrainServiceAlerts/disruption.json", params=0):
        with open(URL) as f:
            data = json.load(f)
        return data

    def scheduler_loop(self, test=True):
        '''
        Scheduler runs this function every 10mins to pull data from LTA API and push into db
        '''

        if test:
            disruption_data = self.pull_from_LTA_TEST_disruption()
        else:
            disruption_data = self.pull_from_LTA(self.disruption_url, params={})

        # Add to disruptions if any
        if disruption_data['value']['Status'] != 1:
            for affected_segment, message in zip(disruption_data["value"]['AffectedSegments'],
                                                 disruption_data["value"]["Message"]):
                stn_data = affected_segment["Stations"].split(',')
                dbAPI.insert_majordisruption_db(self.db_obj, created_at=message["CreatedDate"],
                                                resolved_at=None,
                                                affected_stations=stn_data,
                                                description=message["Content"])
        else:
            res = dbAPI.query_majordisruption_db(self.db_obj)

            if res:
                dbAPI.insert_majordisruption_db(self.db_obj, created_at=res[0].created_at,
                                                resolved_at=timezone.now(),
                                                affected_stations=None,
                                                description=res[0].description)

        for line in self.train_line:
            params = {"TrainLine": line}

            if test:
                realtime_data = self.pull_from_LTA_TEST(line=line)
                forecast_data = self.pull_from_LTA_TEST(line=line)
            else:
                forecast_data = self.pull_from_LTA(self.forecast_url, params=params)
                realtime_data = self.pull_from_LTA(self.realtime_url, params=params)
            try:
                for row in realtime_data['value']:
                    startTime = row['StartTime'].split('T')
                    startTime = ' '.join([startTime[0], startTime[1].split('+')[0]])
                    startTime = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
                    dbAPI.insert_congestion_db(self.db_obj, startTime, self.crowdlevel_dict[row['CrowdLevel']], row['Station'])

                for row in forecast_data['value']:
                    startTime = row['StartTime'].split('T')
                    startTime = ' '.join([startTime[0], startTime[1].split('+')[0]])
                    startTime = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
                    dbAPI.insert_congestionforecast_db(self.db_obj,  startTime, self.crowdlevel_dict[row['CrowdLevel']], row['Station'])
            except:
                print("smth went wrong")
                pass

if __name__ == "__main__":
    manager = APILoaderManager()
    manager.scheduler_loop(test=False)
