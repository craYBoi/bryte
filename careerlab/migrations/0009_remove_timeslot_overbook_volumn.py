# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-08 21:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0008_auto_20160508_2126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeslot',
            name='overbook_volumn',
        ),
    ]
