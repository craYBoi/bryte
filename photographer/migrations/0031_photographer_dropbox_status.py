# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-07 04:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0030_photographer_dropbox_acct'),
    ]

    operations = [
        migrations.AddField(
            model_name='photographer',
            name='dropbox_status',
            field=models.BooleanField(default=False),
        ),
    ]