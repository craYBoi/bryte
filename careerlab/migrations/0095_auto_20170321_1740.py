# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-03-21 22:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0094_auto_20170309_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='checked_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='is_taken_photo',
            field=models.BooleanField(default=False),
        ),
    ]
