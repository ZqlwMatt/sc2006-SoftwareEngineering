# Generated by Django 4.2.5 on 2023-09-26 13:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0009_remove_incidentreport_affected_stations_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="incident",
            old_name="created_at",
            new_name="started_at",
        ),
        migrations.RemoveField(
            model_name="incident",
            name="station",
        ),
        migrations.AddField(
            model_name="incidentreport",
            name="station",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.station",
            ),
            preserve_default=False,
        ),
    ]
