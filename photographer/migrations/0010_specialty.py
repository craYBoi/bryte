# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-12 07:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photographer', '0009_auto_20160112_0703'),
    ]

    operations = [
        migrations.CreateModel(
            name='Specialty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialty_text', models.CharField(choices=[('Headshot', 'hs'), ('Outdoor', 'od'), ('Vintage', 'vt'), ('Indoor', 'id'), ('Portrait', 'pt')], max_length=120)),
                ('photographer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='photographer.Photographer')),
            ],
        ),
    ]
