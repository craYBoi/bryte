# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-17 06:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0011_auto_20160112_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='photographer',
            name='is_student',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]