# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_config_songs_directory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='songs_limit',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='songs_limit_time',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
