# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-15 17:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0015_signup_shoot'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeadshotImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_thumbnail', models.BooleanField(default=False)),
                ('is_watermarked', models.BooleanField(default=False)),
                ('url', models.CharField(max_length=80)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='careerlab.Booking')),
            ],
        ),
    ]
