# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0006_auto_20161231_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='songs_directory_changed',
            field=models.BooleanField(default=False),
        ),
    ]
