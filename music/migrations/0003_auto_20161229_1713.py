# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_playlist_song_changed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='position',
        ),
        migrations.AddField(
            model_name='playlist',
            name='position_changed',
            field=models.BooleanField(default=False),
        ),
    ]
