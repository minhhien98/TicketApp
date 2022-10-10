# Generated by Django 4.0.4 on 2022-09-21 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_userextend_workshop_ticket_alter_userextend_ticket'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userextend',
            name='workshop_ticket',
        ),
        migrations.AddField(
            model_name='userextend',
            name='special_ticket',
            field=models.IntegerField(default=0, verbose_name='Vé đặc biệt'),
        ),
        migrations.AlterField(
            model_name='userextend',
            name='ticket',
            field=models.IntegerField(default=0, verbose_name='Vé thường'),
        ),
    ]