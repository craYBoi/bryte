# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-02-07 18:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0088_nextshoot_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='signup',
            name='is_sub',
            field=models.BooleanField(default=True),
        ),
    ]