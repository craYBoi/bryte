# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-16 22:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('careerlab', '0018_auto_20160615_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImagePurchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('option', models.CharField(choices=[('oh', 'Original Headshot'), ('bt', 'Basic Touchup'), ('pt', 'Premium Touchup'), ('pp', 'Passport Package')], default='og', max_length=2)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('request', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='careerlab.HeadshotImage')),
            ],
        ),
    ]
