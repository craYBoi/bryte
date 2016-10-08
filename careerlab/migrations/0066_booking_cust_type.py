# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-10-08 16:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0065_auto_20161003_0249'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='cust_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'No free nor buy'), (2, 'Free only'), (3, 'Paid customer')], default=1, null=True),
        ),
    ]
