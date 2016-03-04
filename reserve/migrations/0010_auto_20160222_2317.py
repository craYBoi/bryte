# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-22 23:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserve', '0009_auto_20160129_0350'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='business_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='date_range',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]