import json
from base import BaseView

from music.services.playlist import PlayListService
from music.services.song import SongService
from django.core.cache import cache


class StateView(BaseView):

    def post(self, *args, **kwargs):

        state_data = self.request.POST.get("data")
        cache.set("player_state_data", state_data)

        state_data = json.loads(state_data)
        song_finished = state_data["song_finished"]
        if song_finished:
            SongService().play_next_song(is_next=True)

        playlist = PlayListService().get_playlist()

        song_changed = playlist.song_changed
        position_changed = playlist.position_changed

        playlist.song_changed = False
        playlist.position_changed = False
        playlist.save()

        data = {
            "path": playlist.current_song.path,
            "song_changed": song_changed,
            "position_changed": position_changed,
            "position": playlist.position,
            "state": playlist.state,
            "volume": playlist.volume,
        }

        return self.json_response(data)