# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-07 04:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0031_photographer_dropbox_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photographer',
            name='dropbox_status',
        ),
    ]
