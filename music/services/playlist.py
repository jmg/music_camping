from music.services.base import BaseService
from music.models import PlayList


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