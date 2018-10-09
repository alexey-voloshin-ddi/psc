# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-20 10:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import psc.product.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Documentation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('path', models.FileField(upload_to=psc.product.utils.get_document_upload_path)),
                ('type', models.CharField(choices=[('doc', 'doc'), ('docx', 'docx'), ('pdf', 'pdf'), ('csv', 'csv'), ('xls', 'xls'), ('xlsx', 'xlsx'), ('odf', 'odf')], max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('type', models.CharField(choices=[('png', 'png'), ('jpeg', 'jpeg'), ('gif', 'gif')], max_length=4)),
                ('path', models.ImageField(upload_to=psc.product.utils.get_images_upload_path)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('short_description', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('user_path', models.URLField()),
                ('ph_path', models.URLField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
        migrations.AddField(
            model_name='image',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product'),
        ),
        migrations.AddField(
            model_name='documentation',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product'),
        ),
    ]