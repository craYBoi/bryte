# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-22 03:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0075_auto_20161021_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headshotpurchase',
            name='background',
            field=models.PositiveSmallIntegerField(choices=[(1, 'White'), (2, 'Polished Gray'), (3, 'Designer Bricks'), (4, 'Sanguine Blue'), (5, 'Nighttime Black'), (6, 'Light Cream')], default=1),
        ),
    ]