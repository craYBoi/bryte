# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-03 01:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0035_auto_20160703_0148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='dropbox_folder',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='upgrade_folder_path',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]