# Generated by Django 4.0.4 on 2022-05-25 05:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0002_alter_participant_join_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 25, 5, 55, 56, 985285)),
        ),
    ]
