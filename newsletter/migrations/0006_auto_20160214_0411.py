# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-14 04:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0005_auto_20160125_0254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='is_student',
        ),
        migrations.AddField(
            model_name='price',
            name='level',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
