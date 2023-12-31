# Generated by Django 4.2.5 on 2023-09-26 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0007_remove_incident_affected_stations_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="incidentreport",
            name="incident",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="incident_reports",
                to="main.incident",
            ),
        ),
    ]
