# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-13 22:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0020_auto_20160213_2145'),
        ('userprofile', '0002_profile_stripe_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='photographer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to='photographer.Photographer'),
        ),
        migrations.AddField(
            model_name='profile',
            name='refresh_token',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='scope',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='stripe_publishable_key',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='stripe_user_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
