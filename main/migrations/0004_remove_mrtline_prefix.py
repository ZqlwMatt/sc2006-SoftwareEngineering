# Generated by Django 4.2.5 on 2023-09-26 07:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_rename_reported_at_incident_created_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mrtline",
            name="prefix",
        ),
    ]
