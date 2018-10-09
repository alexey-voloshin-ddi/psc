# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-23 12:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_image_crop_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='crop_type',
            field=models.CharField(choices=[('th', 'Thumbnail'), ('pl', 'Product Listing'), ('pr', 'Product Detail')], max_length=2),
        ),
        migrations.AlterField(
            model_name='video',
            name='ph_path',
            field=models.URLField(blank=True, null=True),
        ),
    ]
