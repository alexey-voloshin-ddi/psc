# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-24 09:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_image_product_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentation',
            name='type',
            field=models.CharField(choices=[('doc', 'doc'), ('docx', 'docx'), ('pdf', 'pdf'), ('csv', 'csv'), ('xls', 'xls'), ('xlsx', 'xlsx'), ('odf', 'odf'), ('odt', 'odt')], max_length=4),
        ),
        migrations.AlterField(
            model_name='product',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.Company'),
        ),
    ]
