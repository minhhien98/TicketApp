# Generated by Django 4.0.4 on 2022-06-23 12:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0006_participant_quantity_alter_participant_join_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='join_date',
        ),
        migrations.AddField(
            model_name='participant',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 23, 12, 14, 7, 847807)),
        ),
    ]
