# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-28 17:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0078_auto_20161025_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='headshotorder',
            name='feedback_rating',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
