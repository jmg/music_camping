# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network_type', models.CharField(default=b'Local', max_length=20, choices=[(b'Internet', b'Internet'), (b'Local', b'Local')])),
                ('song_selection_type', models.CharField(default=b'Queue', max_length=20, choices=[(b'Queue', b'Queue'), (b'Vote', b'Vote')])),
                ('songs_limit', models.PositiveIntegerField()),
                ('songs_limit_time', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PlayList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=50, null=True, blank=True)),
                ('volume', models.CharField(max_length=50, null=True, blank=True)),
                ('position', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlayListSong',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort', models.PositiveIntegerField(default=1)),
                ('playlist', models.ForeignKey(to='music.PlayList')),
            ],
            options={
                'ordering': ('sort',),
            },
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=2000)),
                ('name', models.CharField(max_length=1000)),
                ('artist', models.CharField(max_length=1000)),
                ('genre', models.CharField(max_length=1000)),
                ('album', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.CharField(max_length=1000)),
                ('submitted_songs', models.ManyToManyField(to='music.Song')),
            ],
        ),
        migrations.AddField(
            model_name='playlistsong',
            name='song',
            field=models.ForeignKey(to='music.Song'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='current_song',
            field=models.OneToOneField(null=True, blank=True, to='music.Song'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='songs',
            field=models.ManyToManyField(related_name='playlist_songs', through='music.PlayListSong', to='music.Song'),
        ),
    ]
