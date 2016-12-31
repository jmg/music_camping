from music.services.base import BaseService
from music.models import PlayList, PlayListSong


class PlayListService(BaseService):

    entity = PlayList

    def get_playlist(self):

        playlist, created = self.get_or_create(id=1)
        if created:
            playlist.volume = 100
            playlist.position = 0
            playlist.state = "Not Playing"
            playlist.save()

        return playlist

    def clear(self):

        playlist = self.get_playlist()
        playlist_songs = PlayListSong.objects.filter(playlist=playlist)

        for playlist_song in playlist_songs:
            playlist_song.delete()