# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-15 17:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0016_headshotimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='headshotimage',
            name='is_deliverable',
            field=models.BooleanField(default=False),
        ),
    ]
