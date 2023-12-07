# Generated by Django 4.2.5 on 2023-10-28 03:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0013_alter_notificationpreference_stations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notificationpreference",
            name="day_time",
        ),
        migrations.AddField(
            model_name="notificationpreference",
            name="day",
            field=models.CharField(
                choices=[
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
                ],
                default="",
                max_length=100,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notificationpreference",
            name="sent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="notificationpreference",
            name="specific_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="notificationpreference",
            name="time",
            field=models.TimeField(default="11:30"),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="NotificationPreferenceTiming",
        ),
    ]