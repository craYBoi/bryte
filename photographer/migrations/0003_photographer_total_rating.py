# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-06 10:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0002_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='photographer',
            name='total_rating',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]