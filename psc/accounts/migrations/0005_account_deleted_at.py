# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-25 10:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_account_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
