import requests
import json



def find_stn_record(json_data, stn):
        for i in json_data['value']:
            if i["Station"] == stn:
                return i

def pull_from_LTA(train_line):

    #URL = "http://datamall2.mytransport.sg/ltaodataservice/PCDForecast"
    URL = "http://datamall2.mytransport.sg/ltaodataservice/PCDRealTime"
    params = { "TrainLine": train_line}
    _get_auth_headers = {'accept': 'application/json',
                         "AccountKey": "qfmORDTTRTSy8qiKeNAzkg=="}

    response = requests.get(URL, headers=_get_auth_headers, params=params)
    print("DATA PULLED FROM LTAMALL", response.text)
    return response.json()


# file = r"C:\Users\Creaton\Downloads\realtime.json"
# with open(file) as f:
#     data = json.load(json_data)
#     for i in data['value']:
#         if i["Station"] == 'NS1':
#             print(i)