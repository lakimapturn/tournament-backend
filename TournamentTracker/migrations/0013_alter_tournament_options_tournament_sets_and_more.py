# Generated by Django 4.0.4 on 2022-12-11 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TournamentTracker', '0012_tournament_cutoff_month'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tournament',
            options={'ordering': ('-start_date', '-end_date')},
        ),
        migrations.AddField(
            model_name='tournament',
            name='sets',
            field=models.PositiveSmallIntegerField(blank=True, default=3, null=True),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='points_per_win',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
