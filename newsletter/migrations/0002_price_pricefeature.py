# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-16 07:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('price', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PriceFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_text', models.CharField(max_length=200)),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter.Price')),
            ],
        ),
    ]
