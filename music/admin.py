from django.contrib import admin

from music.models import *

admin.site.register(Song)
admin.site.register(PlayList)
admin.site.register(PlayListSong)
