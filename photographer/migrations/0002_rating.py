# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-06 07:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField()),
                ('comment', models.TextField()),
                ('photographer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='photographer.Photographer')),
            ],
        ),
    ]
