# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-14 04:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0023_auto_20160214_0136'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='level',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
