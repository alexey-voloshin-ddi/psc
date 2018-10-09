# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-24 11:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_auto_20170724_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='crop_type',
            field=models.CharField(choices=[('th', 'Thumbnail'), ('pl', 'Product Listing'), ('pr', 'Product Detail'), ('co', 'Company Logo')], max_length=2),
        ),
    ]