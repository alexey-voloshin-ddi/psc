# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-07 12:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_image_is_edited_outside'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='company',
        ),
    ]
