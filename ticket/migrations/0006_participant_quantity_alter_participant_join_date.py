# Generated by Django 4.0.4 on 2022-06-23 11:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0005_alter_participant_join_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='participant',
            name='join_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 23, 11, 20, 46, 680174)),
        ),
    ]