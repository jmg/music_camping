#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_tesseract.settings")

    from django.core.management import execute_from_command_line

    from music.services.song import SongService
    SongService().check_if_song_finished()

    execute_from_command_line(sys.argv)
