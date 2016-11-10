# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-29 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0080_auto_20161029_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headshotpurchase',
            name='background',
            field=models.PositiveSmallIntegerField(choices=[(1, 'White'), (2, 'Polished Gray'), (3, 'Designer Bricks'), (4, 'Sanguine Blue'), (5, 'Nighttime Black'), (6, 'Light Cream'), (7, 'Frosty Blue'), (8, 'Riverside Blue'), (9, 'Airy Gray'), (10, 'Vibrant Orange'), (11, '31st Story Office'), (12, 'Eclectic Bookcase'), (13, 'Firm Hallway'), (14, 'Urban Walkway')], default=1),
        ),
    ]