# Generated by Django 4.0.4 on 2022-07-02 18:50

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ticket', '0008_alter_participant_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='participant',
            options={'verbose_name': 'Người tham gia', 'verbose_name_plural': 'Người tham gia'},
        ),
        migrations.AlterField(
            model_name='participant',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.utcnow, verbose_name='Ngày tham gia'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='quantity',
            field=models.IntegerField(default=1, verbose_name='Số lượng đăng ký'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Người dùng'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='workshop_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.workshop', verbose_name='Workshop'),
        ),
        migrations.AlterField(
            model_name='workshop',
            name='date',
            field=models.DateTimeField(verbose_name='Ngày diễn ra'),
        ),
        migrations.AlterField(
            model_name='workshop',
            name='name',
            field=models.CharField(max_length=30, verbose_name='Tên Workshop'),
        ),
        migrations.AlterField(
            model_name='workshop',
            name='slot',
            field=models.IntegerField(verbose_name='Số lượng chỗ trống'),
        ),
    ]