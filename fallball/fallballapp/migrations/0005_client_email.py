# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-09 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fallballapp', '0004_async_client_provisioning'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='email',
            field=models.EmailField(blank=True, default=None, max_length=254, null=True),
        ),
    ]
