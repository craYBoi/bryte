# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-03 03:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0012_auto_20160303_0234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='class_name',
        ),
    ]
