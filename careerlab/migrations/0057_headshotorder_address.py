# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-09-21 01:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0056_auto_20160921_0113'),
    ]

    operations = [
        migrations.AddField(
            model_name='headshotorder',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
