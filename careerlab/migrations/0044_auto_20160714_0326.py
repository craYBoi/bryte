# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-14 03:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0043_auto_20160714_0157'),
    ]

    operations = [
        migrations.RenameField(
            model_name='signup',
            old_name='headshot_for',
            new_name='area_of_study',
        ),
        migrations.RenameField(
            model_name='signup',
            old_name='school_year',
            new_name='program_progress',
        ),
    ]
