# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_auto_20161229_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='position',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
