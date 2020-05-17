# Generated by Django 3.0.5 on 2020-05-10 18:53

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oth', '0006_auto_20200510_1829'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='level',
            name='accuracy',
        ),
        migrations.AlterField(
            model_name='level',
            name='image',
            field=models.ImageField(default='images/level1.jpg', upload_to='images/<django.db.models.fields.IntegerField>'),
        ),
        migrations.AlterField(
            model_name='notif',
            name='date',
            field=models.DateTimeField(verbose_name=datetime.datetime(2020, 5, 10, 18, 53, 20, 146771)),
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('l_number', models.IntegerField()),
                ('image', models.ImageField(blank=True, default='images/level1.jpg', upload_to='images')),
                ('sentiment', models.IntegerField()),
                ('facial_expression', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
