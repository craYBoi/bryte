# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-25 03:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('newsletter', '0005_auto_20160125_0254'),
        ('userprofile', '0002_profile_stripe_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('price', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter.Price')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userprofile.Profile')),
            ],
        ),
    ]
