# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-26 03:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0015_auto_20160526_0303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactsale',
            name='amount',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='contactsale',
            name='category',
            field=models.CharField(max_length=20),
        ),
    ]
