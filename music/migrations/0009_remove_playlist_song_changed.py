# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0008_auto_20170101_0159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='song_changed',
        ),
    ]
