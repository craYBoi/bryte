# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-07 17:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0038_nextshoot_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeslot',
            name='active',
        ),
    ]