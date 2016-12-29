import os
import mimetypes
from music.models import Song
from music.services.song import SongService
import eyeD3


class ConfigService(object):

    def save_songs_for_dir(self, directory):

        songs = []
        for directory, sub_folders, files in os.walk(directory):
            for file in files:
                if self.valid_format(file):
                    path = os.path.join(directory, file)

                    tag = eyeD3.Tag()
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