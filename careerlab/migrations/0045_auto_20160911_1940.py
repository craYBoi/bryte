# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-09-11 19:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0044_auto_20160714_0326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='area_of_study',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='professional_path',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='program_progress',
        ),
        migrations.RemoveField(
            model_name='signup',
            name='area_of_study',
        ),
        migrations.RemoveField(
            model_name='signup',
            name='professional_path',
        ),
        migrations.RemoveField(
            model_name='signup',
            name='program_progress',
        ),
    ]
