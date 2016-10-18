# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-17 16:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0071_headshotorder_touchup_folder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headshotpurchase',
            name='background',
            field=models.PositiveSmallIntegerField(choices=[(1, 'White'), (2, 'Polished Gray'), (3, 'Designer Bricks'), (4, 'Sanguine Blue'), (5, 'Nighttime Black'), (6, 'Whipped Cream')], default=1),
        ),
    ]
