# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_playlist_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='songs_directory',
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
    ]
