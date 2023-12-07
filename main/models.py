import pandas as pd
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe

from sc2006_project.utils import GroupConcat

from django.db.models import Count

class StationManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(codes=GroupConcat("line_stations__station_code"))
            .order_by("name")
        )


class MRTLine(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    code = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class MRTLineStation(models.Model):
    mrt_line = models.ForeignKey(
        "MRTLine", on_delete=models.CASCADE, related_name="line_stations", null=False
    )
    station = models.ForeignKey(
        "Station", on_delete=models.CASCADE, null=False, related_name="line_stations"
    )
    station_code = models.CharField(max_length=5, null=False, unique=True)

    def __str__(self):
        return f"{self.station.name} ({self.station_code})"

    class Meta:
        unique_together = ("mrt_line", "station")

    # def get_congestion_rating(self):
    #     """
    #     Note that this method is specific to train stations on a certain MRT line. Interchanges have
    #     multiple congestion ratings, one for each MRT line.
    #     :return int rating: The congestion rating of a station platform, based on LTA and user-submitted data.
    #     """
    #     pass


class Station(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    train_line_stations = models.ManyToManyField(
        MRTLine, through=MRTLineStation, through_fields=("station", "mrt_line")
    )
    objects = StationManager()

    def __str__(self):
        if hasattr(self, "codes"):  # provided in get_queryset
            codes = self.codes
        else:
            codes = "/".join(self.line_stations.values_list("station_code", flat=True))
        return f"{self.name} ({codes})"

    # def get_all_congestion_ratings(self):
    #     """
    #     Note that this method is specific to train stations on a certain MRT line. Interchanges have
    #     multiple congestion ratings, one for each MRT line.
    #     :return dict[str, int] ratings: Each platform at a Station with its corresponding congestion rating.
    #     """
    #     pass

class NotificationPreference(models.Model):
    DAY_CHOICES = [
        ["specific_date", "On a specific date"],
        ["weekdays", "Every weekday"],
        ["weekends", "Every weekend"],
        ["mon", "On Mondays"],
        ["tue", "On Tuesdays"],
        ["wed", "On Wednesdays"],
        ["thu", "On Thursdays"],
        ["fri", "On Fridays"],
        ["sat", "On Saturdays"],
        ["sun", "On Sundays"],

    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, related_name="preferences"
    )
    day = models.CharField(
        null=False,
        max_length=100,
        choices=DAY_CHOICES
    )
    specific_date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=False)
    stations = models.ManyToManyField(Station)
    rule = models.CharField(
        max_length=100,
        choices=[
            ["everyday", "Every day at this time"],
            ["disruption", "When there is a disruption"],
        ],
    )
    sent = models.BooleanField(null=False, default=False)

    # @classmethod
    # def get_preferences_for_users(cls, user):
    #     """
    #     :return dict[str, int] ratings: Each platform at a Station with its corresponding congestion rating.
    #     """

class DisruptionAffectedStation(models.Model):
    station = models.ForeignKey(
        "MRTLineStation", on_delete=models.CASCADE, related_name="disruption_affected_stations"
    )
    disruption = models.ForeignKey(
        "MajorDisruption",
        on_delete=models.CASCADE,
        related_name="disruption_affected_stations",
    )


class IncidentReportAffectedStation(models.Model):
    station = models.ForeignKey(
        "Station",
        on_delete=models.CASCADE,
        related_name="incident_report_affected_stations",
    )
    incident_report = models.ForeignKey(
        "IncidentReport",
        on_delete=models.CASCADE,
        related_name="incident_report_affected_stations",
    )


class MajorDisruption(models.Model):
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    resolved_at = models.DateTimeField(null=True)
    affected_stations = models.ManyToManyField(
        MRTLineStation,
        through="DisruptionAffectedStation",
        through_fields=("disruption", "station"),
        verbose_name="affected station(s)",
    )
    description = models.TextField(null=False)

    @classmethod
    def insert_db(cls, created_at, resolved_at, affected_stations, description):
        obj, created = MajorDisruption.objects.get_or_create(created_at=created_at, defaults={"resolved_at": resolved_at, 'description': description})
        if resolved_at:
            obj.resolved_at=resolved_at
            obj.save()
        if created:
            for i in affected_stations:
                stn_code = MRTLineStation.objects.get(station_code=i)
                DisruptionAffectedStation.objects.get_or_create(station=stn_code, disruption=obj)


class Incident(models.Model):
    station = models.ForeignKey(Station, null=True, on_delete=models.CASCADE)
    started_at = models.DateTimeField(
        null=False
    )  # same as reported_at of first related IncidentReport
    escalated_at = models.DateTimeField(
        auto_now_add=True, null=True
    )  # after threshold of incident reports is reached
    resolved_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="resolved_incidents"
    )
    resolved_at = models.DateTimeField(null=True)

    TIME_THRESHOLD = 24
    # incident reports within this many hours can be treated as the same incident

    REPORTS_THRESHOLD = 5
    # at least this many reports must be made to trigger a probable incident

    @property
    def status(self):
        if self.resolved_by and self.resolved_at:
            resolved_at = timezone.localtime(self.resolved_at).strftime("%d %b %Y, %I:%M %p")
            return f"Resolved: {resolved_at}, by {self.resolved_by}"
        if self.announcements.exists():
            latest_announcement = self.announcements.latest("added_at")
            added_at = timezone.localtime(latest_announcement.added_at).strftime("%d %b %Y, %I:%M %p")
            return f"Verified; Latest announcement: {added_at}, by {latest_announcement.added_by}"
        return "Unverified"
    @property
    def manage_button(self):
        if self.resolved_by and self.resolved_at:
            return ""
        url = reverse("main:verify_reports", kwargs={"pk": self.id})
        return mark_safe(f"<a href='{url}'>Manage</a>")


class IncidentReport(models.Model):
    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, null=True, related_name="incident_reports"
    )
    reported_at = models.DateTimeField(auto_now_add=True, null=False)
    reported_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="incident_reports"
    )
    description = models.TextField(null=False)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=False)


class Announcement(models.Model):
    added_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    added_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="announcements"
    )
    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, null=False, related_name="announcements"
    )
    content = models.TextField(null=False, blank=False)


class Congestion(models.Model):
    added_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True
    )  # if blank, then source is LTA API
    station = models.ForeignKey(
        MRTLineStation, on_delete=models.CASCADE, null=False, related_name="congestion_ratings"
    )
    time = models.DateTimeField(auto_now_add=True, null=False)
    congestion = models.IntegerField(null=False)

    CONGESTION_KEY = {0: 'l',
                      1: 'm',
                      2: 'h',
                      999: 'na'}

    @classmethod
    def query_db_json(cls):
        congestion_entries = Congestion.objects.values("station__station_code", "station__station__name", "station__station_id", "station__mrt_line__code", "congestion", "station__mrt_line__name")
        df = pd.DataFrame(congestion_entries)

        df["congestion"] = df["congestion"].replace(cls.CONGESTION_KEY)
        df["congestion_entry"] = df.apply(lambda row: {
            "StationName": row['station__station__name'],
            "Station": f"{row['station__station__name']} ({row['station__station_code']})",
            "StationCode": row['station__station_code'],
            "CrowdLevel": row["congestion"],
            "StationID": row['station__station_id'],
        }, axis=1)

        output_df = df.groupby("station__mrt_line__code").agg({'congestion_entry': lambda x: list(x),
                                                               'station__mrt_line__name': lambda x: x.iloc[0] if len(x) else None})

        output_dict = dict(zip(output_df.index, zip(output_df["congestion_entry"], output_df["station__mrt_line__name"])))

        return {k: {"value": v[0], "train_line_name": v[1]} for k, v in output_dict.items() if v}

    @classmethod
    def insert_db(cls,  time, congestion, station_code):
        stn_code = MRTLineStation.objects.get(station_code=station_code)
        #stn_code = Station.objects.get(line_stations=stn_code)
        obj, created = Congestion.objects.get_or_create(station=stn_code, defaults={"time": time, "congestion": congestion})

class CongestionForecast(models.Model):
    station = models.ForeignKey(
        MRTLineStation,
        on_delete=models.CASCADE,
        null=False,
        related_name="congestion_forecasts",
    )
    # added_at = models.DateTimeField(auto_now_add=True, null=False)
    time = models.DateTimeField(null=False)
    forecast = models.IntegerField(null=False)

    @classmethod
    def insert_db(cls,  time, forecast, station_code):
        stn_code = MRTLineStation.objects.get(station_code=station_code)
        CongestionForecast.objects.get_or_create(station=stn_code, defaults={"time":time, "forecast":forecast})

