# Generated by Django 4.0.4 on 2022-10-29 09:10

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0019_alter_workshop_icon_alter_workshop_ticket_template'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workshop',
            name='icon',
            field=django_resized.forms.ResizedImageField(crop=None, default='ticket/img/icon-default-300.png', force_format=None, keep_meta=True, quality=-1, scale=None, size=[90, 90], upload_to='ticket/icon', verbose_name='icon'),
        ),
        migrations.AlterField(
            model_name='workshop',
            name='ticket_template',
            field=django_resized.forms.ResizedImageField(crop=None, default='ticket/img/ticket_template.png', force_format=None, keep_meta=True, quality=-1, scale=None, size=[720, 1280], upload_to='ticket/ticket_template', verbose_name='Ảnh vé'),
        ),
    ]
