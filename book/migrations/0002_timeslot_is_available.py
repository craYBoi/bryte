# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-22 21:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]