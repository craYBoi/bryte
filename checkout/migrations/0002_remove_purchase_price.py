# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-25 16:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='price',
        ),
    ]
