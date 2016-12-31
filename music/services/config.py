import os
import mimetypes
from music.models import Config
from music.services.base import BaseService
from music.services.song import SongService
try:
    from eyed3.core import Tag
except:
    from eyeD3 import Tag


class ConfigService(BaseService):

    entity = Config

    def save(self, data):

        config = self.get_or_new(id=1)
        config.songs_directory_changed = True
        config.songs_directory = data["songs_directory"]
        config.save()

    def save_songs(self, songs_paths):

        for path in songs_paths:

            tag = Tag()
            tag.link(path)

            song, created = SongService().get_or_create(
                path=path,
                defaults={
                    "name": tag.getTitle(),
                    "artist": tag.getArtist(),
                    "album": tag.getAlbum(),
                }
            )

    def save_songs_for_dir(self, directory):

        songs = []
        for directory, sub_folders, files in os.walk(directory):
            for file in files:
                if self.valid_format(file):
                    path = os.path.join(directory, file)

                    tag = Tag()
                    tag.link(path)

                    song, created = Song.objects.get_or_create(
                        path=path,
                        defaults={
                            "name": tag.getTitle(),
                            "artist": tag.getArtist(),
                            "album": tag.getAlbum(),
                        }
                    )
                    song.save()
                    if created:
                        songs.append(song)

        return songs

    def valid_format(self, name):

        validFormats = ['.mp3','.wav','.wma', '.avi', '.ogg', '.flac']
        for format in validFormats:
            if name.find(format) != -1:
                return True
        return False