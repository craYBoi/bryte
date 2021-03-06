# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-11 09:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0007_auto_20160109_1321'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=50)),
                ('photographer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='photographer.Photographer')),
            ],
        ),
        migrations.CreateModel(
            name='PackageFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_text', models.CharField(max_length=120)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='photographer.Package')),
            ],
        ),
    ]
