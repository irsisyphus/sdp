# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-15 02:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_component_localposition'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='localPosition',
            field=models.IntegerField(default=0),
        ),
    ]
