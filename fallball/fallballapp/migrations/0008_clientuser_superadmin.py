# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-06-05 12:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fallballapp', '0007_postalcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientuser',
            name='superadmin',
            field=models.BooleanField(default=False),
        ),
    ]
