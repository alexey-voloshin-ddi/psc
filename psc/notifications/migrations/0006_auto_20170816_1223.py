# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-16 12:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0005_auto_20170803_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.SmallIntegerField(choices=[(1, 'User Approved'), (2, 'Company Approved'), (3, 'Company Deny'), (4, 'Product Approved'), (5, 'Product Deny'), (6, 'Account Multiple users activated'), (7, 'Account Multiple company activated'), (8, 'Invited user registered'), (9, 'User Deny'), (10, 'User Confirmed'), (11, 'User Removed'), (12, 'Company Removed'), (13, 'Product Removed')]),
        ),
    ]
