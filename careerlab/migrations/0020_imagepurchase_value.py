# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-17 01:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0019_imagepurchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagepurchase',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
            preserve_default=False,
        ),
    ]