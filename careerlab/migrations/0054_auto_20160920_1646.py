# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-09-20 16:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0053_auto_20160914_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headshotpurchase',
            name='background',
            field=models.PositiveSmallIntegerField(choices=[(1, 'White'), (2, 'Polished Gray'), (3, 'Designer Bricks'), (4, 'Sanguine Blue'), (5, 'Nighttime Black')], default=1),
        ),
        migrations.AlterField(
            model_name='headshotpurchase',
            name='touchup',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Free'), (2, 'Upgraded'), (3, 'Customized')], default=1),
        ),
    ]