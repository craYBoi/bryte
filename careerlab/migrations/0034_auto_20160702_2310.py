# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-02 23:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0033_auto_20160702_1656'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagepurchase',
            name='address',
        ),
        migrations.RemoveField(
            model_name='imagepurchase',
            name='request',
        ),
        migrations.AlterField(
            model_name='imagepurchase',
            name='option',
            field=models.CharField(choices=[('fh', 'Free Headshot'), ('pu', 'Professional Upgrade'), ('ph', 'Premium Headshot'), ('pp', 'Premium Portrait')], default='pu', max_length=2),
        ),
    ]