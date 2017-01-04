import json
from base import BaseView

from music.services.playlist import PlayListService
from music.services.song import SongService
from music.services.config import ConfigService
from django.core.cache import cache


class StateView(BaseView):

    def post(self, *args, **kwargs):

        try:
            state_data = self.request.POST.get("data")
            cache.set("player_state_data", state_data)
            state_data = json.loads(state_data)
            song_finished = state_data["song_finished"]
        except:
            song_finished = False

        if song_finished:
            SongService().play_next_song(is_next=True)

        playlist = PlayListService().get_playlist()
        position_changed = playlist.position_changed
        playlist.position_changed = False

        if position_changed:
            playlist.save()

        config = ConfigService().get_one(id=1)
        songs_directory_changed = config.songs_directory_changed
        config.songs_directory_changed = False

        if songs_directory_changed:
            config.save()

        data = {
            "path": playlist.current_song.path if playlist.current_song else None,
            "position_changed": position_changed,
            "position": playlist.position,
            "state": playlist.state,
            "volume": playlist.volume,
            "songs_directory_changed": songs_directory_changed,
            "songs_directory": config.songs_directory,
        }

        return self.json_response(data)

    get = post


class SaveSongsView(BaseView):

    def post(self, *args, **kwargs):

        songs = json.loads(self.request.POST.get("songs"))
        ConfigService().save_songs(songs)

        return self.json_response({"status": "success"})


class RemoveMediaSongsView(BaseView):

    def post(self, *args, **kwargs):

        SongService().remove_media_songs()

        return self.json_response({"status": "success"})