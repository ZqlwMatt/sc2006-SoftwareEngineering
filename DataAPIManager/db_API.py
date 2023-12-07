import datetime
import os
from django import setup
from itertools import chain

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sc2006_project.settings")
setup()

from main.models import *
from django.db.models import Count

class dbAPI():

    def __init__(self):
        return

    def insert_congestion_db(self, time, congestion, station_code):
        Congestion.insert_db(time, congestion, station_code)

    def query_congestion_db(self, station):
        return Congestion.objects.filter(station__station_id=station)[0]

    def insert_congestionforecast_db(self, time, forecast, station_code):
        CongestionForecast.insert_db(time, forecast, station_code)

    def query_congestionforecast_db(self, station):
        return CongestionForecast.objects.filter(station__station_id=station)[0]

    def insert_majordisruption_db(self, created_at, resolved_at, affected_stations, description):
        MajorDisruption.insert_db(created_at, resolved_at, affected_stations, description)

    def query_majordisruption_db(self):
        return MajorDisruption.objects.filter(resolved_at__isnull=True, created_at__isnull=False)

    def count_reports(self):
        return Incident.objects.annotate(num_announcements=Count("announcements")).filter(num_announcements__gt=0)

    def query_announcements_db(self):
        return Announcement.objects.values('incident__station_id', "content")

    def getPeopleToNotify(self, test=False, time=0):
        # app_db.main_notificationpreferencetiming

        if not test:
            # Get current time
            present = datetime.datetime.now()
            present_time = present.time()
            present_day = present.today().weekday()
            present_date = present.date()

        # For test
        else:
            present = datetime.datetime(2023, 10, 26, 12, 0, 0)
            present_time = present.time()
            present_day = present.weekday()
            present_date = present.date()

        # find time that is 20mins from now
        time_change = datetime.timedelta(minutes=20)
        future = present + time_change
        future_time, future_day = future.time(), future.weekday()
        future_date = present.date()

        specific_date_cases = NotificationPreference.objects.filter(time__gte=present_time,
                                                         time__lte=future_time,
                                                         day='specific_date',
                                                         specific_date__range=[present_date, future_date])

        if specific_date_cases:
            data = specific_date_cases
        else:
            data = []

        if present_day >= 0 and present_day <= 4:

            # Get lists of people to notify at current time
            weekdays = ['mon', 'tue', 'wed', 'thu', 'fri']
            days = [weekdays[present_day]] + ["weekdays", "everyday"]

            data = list(chain(data, NotificationPreference.objects.filter(time__gte=present_time,
                                                         time__lte=future_time,
                                                         day__in=days)))
        else:
            # Get lists of people to notify at current time
            weekends = ['sat', 'sun']
            days = [weekends[present_day - 5]] + ["weekends", "everyday"]
            data = list(chain(data, NotificationPreference.objects.filter(time__gte=present_time,
                                                         time__lte=future_time,
                                                         day__in=days)))

        info = []
        # Query emails of people to send notifs to
        for row in data:
            if row is None:
                break
            id = row.user_id
            email = User.objects.get(id=id).email
            #preferrence = NotificationPreference.objects.filter(user_id=id)
            #for x in preferrence:
            preferred_stn_id = row.stations.values('id')
            preferred_stn_name = row.stations.get()
            rule = row.rule
            info.append({'id': id, 'email': email, 'stn_id': preferred_stn_id[0]['id'],  'stn': preferred_stn_name, 'rule':rule})
        return info

# Driver Code
if __name__ == "__main__":

    db = dbAPI()
    res = Congestion.query_db_json()




