# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-02-08 23:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0090_signup_hash_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='nextshoot',
            name='noshow_to_signup',
            field=models.BooleanField(default=False),
        ),
    ]