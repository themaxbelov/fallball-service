# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-27 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fallballapp', '0002_clientuser_profile_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientuser',
            name='password',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
