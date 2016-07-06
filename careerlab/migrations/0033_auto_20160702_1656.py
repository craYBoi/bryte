# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-02 16:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0032_booking_show_up'),
    ]

    operations = [
        migrations.RenameField(
            model_name='headshotimage',
            old_name='is_deliverable',
            new_name='is_fav',
        ),
        migrations.RenameField(
            model_name='headshotimage',
            old_name='is_fullsize',
            new_name='is_portrait',
        ),
        migrations.RenameField(
            model_name='headshotimage',
            old_name='is_premium',
            new_name='is_raw',
        ),
        migrations.RenameField(
            model_name='headshotimage',
            old_name='is_watermarked',
            new_name='is_top',
        ),
        migrations.RenameField(
            model_name='headshotimage',
            old_name='thumbnail_url',
            new_name='o_url',
        ),
        migrations.RemoveField(
            model_name='headshotimage',
            name='original_url',
        ),
        migrations.AddField(
            model_name='headshotimage',
            name='wo_url',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='headshotimage',
            name='wt_url',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
