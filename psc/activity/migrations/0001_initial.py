# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-26 12:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LogLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(choices=[(1, 'Created'), (2, 'Edited')])),
                ('instance_type', models.SmallIntegerField(choices=[(1, 'Product'), (2, 'User'), (3, 'Company')])),
                ('instance_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='logline',
            name='summary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.Summary'),
        ),
        migrations.AddField(
            model_name='logline',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
