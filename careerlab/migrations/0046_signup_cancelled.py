# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-09-11 19:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0045_auto_20160911_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
    ]
