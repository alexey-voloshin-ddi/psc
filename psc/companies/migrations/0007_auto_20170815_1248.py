# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-15 12:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0006_companyimages'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='companyimages',
            options={'verbose_name': 'Image', 'verbose_name_plural': 'Images'},
        ),
    ]
