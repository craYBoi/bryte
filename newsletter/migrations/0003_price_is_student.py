# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-16 08:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0002_price_pricefeature'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='is_student',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]