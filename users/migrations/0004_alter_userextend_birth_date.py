# Generated by Django 4.0.4 on 2022-06-02 06:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_userextend_birth_date_alter_userextend_parish_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userextend',
            name='birth_date',
            field=models.DateField(default=datetime.datetime(2022, 6, 2, 6, 9, 54, 37727, tzinfo=utc)),
        ),
    ]
