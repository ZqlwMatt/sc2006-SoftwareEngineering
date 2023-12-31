# Generated by Django 4.2.5 on 2023-10-31 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0016_alter_majordisruption_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="congestionforecast",
            name="station",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="congestion_forecasts",
                to="main.mrtlinestation",
            ),
        ),
        migrations.AlterField(
            model_name="disruptionaffectedstation",
            name="station",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="disruption_affected_stations",
                to="main.mrtlinestation",
            ),
        ),
        migrations.AlterField(
            model_name="majordisruption",
            name="affected_stations",
            field=models.ManyToManyField(
                through="main.DisruptionAffectedStation",
                to="main.mrtlinestation",
                verbose_name="affected station(s)",
            ),
        ),
    ]
