# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-22 06:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0076_auto_20161021_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headshotpurchase',
            name='special_request',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
