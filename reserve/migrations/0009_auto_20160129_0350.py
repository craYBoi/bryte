# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-29 03:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reserve', '0008_reservation_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='price',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='newsletter.Price'),
        ),
    ]
