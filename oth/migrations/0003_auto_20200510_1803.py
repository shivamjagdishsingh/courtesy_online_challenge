# Generated by Django 3.0.5 on 2020-05-10 18:03

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('oth', '0002_auto_20200510_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='level',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notif',
            name='date',
            field=models.DateTimeField(verbose_name=datetime.datetime(2020, 5, 10, 18, 3, 6, 774614)),
        ),
    ]
