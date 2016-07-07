# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-04 05:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecolex', '0007_auto_20160418_2046'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('body_en', models.TextField()),
                ('body_es', models.TextField()),
                ('body_fr', models.TextField()),
            ],
        ),
    ]