# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-12 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0040_nextshoot_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='headshot_for',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='professional_path',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='school_year',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
