# Generated by Django 4.2.5 on 2023-10-31 16:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0019_alter_mrtline_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="announcement",
            name="content",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]