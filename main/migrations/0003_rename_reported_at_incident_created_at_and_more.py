# Generated by Django 4.2.5 on 2023-09-26 07:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0002_mrtline_remove_station_station_codes_mrtlinestation_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="incident",
            old_name="reported_at",
            new_name="created_at",
        ),
        migrations.RemoveField(
            model_name="incident",
            name="reported_by",
        ),
        migrations.AddField(
            model_name="announcement",
            name="added_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="announcements",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="incident",
            name="escalated_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="incident",
            name="resolved_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="incidentreport",
            name="reported_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="incident_reports",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="mrtline",
            name="name",
            field=models.CharField(max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="mrtline",
            name="prefix",
            field=models.CharField(max_length=3, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="mrtlinestation",
            name="station_code",
            field=models.CharField(max_length=5, unique=True),
        ),
        migrations.AlterField(
            model_name="station",
            name="station_name",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name="mrtlinestation",
            unique_together={("mrt_line", "station")},
        ),
        migrations.CreateModel(
            name="IncidentReportAffectedStation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "incident_report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.incidentreport",
                    ),
                ),
                (
                    "station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incident_reports",
                        to="main.station",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="incidentreport",
            name="affected_stations",
            field=models.ManyToManyField(
                through="main.IncidentReportAffectedStation", to="main.station"
            ),
        ),
    ]