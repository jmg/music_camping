from base import BaseView
from music.services.song import SongService
from music.models import PlayList, Song, PlayListSong
import threading


class PlayingView(BaseView):

    url = r"^playlist$"

    def get(self, *args, **kwrags):

        playlist, _ = PlayList.objects.get_or_create(id=1)
        return self.render_to_response({"playlist": playlist, "player": SongService().player})


class ChangeSongView(BaseView):

    def post(self, *args, **kwrags):

        is_next = self.request.POST.get("next") is not None
        is_prev = self.request.POST.get("prev") is not None

        try:
            playlist_song = SongService().change_song(is_next=is_next, is_prev=is_prev)
        except Exception, e:
            return self.json_response({"error": str(e)})

        return self.response(playlist_song.song.to_json())


class PlayView(BaseView):

    def post(self, *args, **kwrags):

        SongService().play_song(self.request.POST.get("song_id"))

        return self.response("ok")


class StopView(BaseView):

    def post(self, *args, **kwrags):

        SongService().player.stop()
        return self.response("ok")


class PauseView(BaseView):

    def post(self, *args, **kwrags):

        SongService().player.pause()
        return self.response("ok")


class SelectView(BaseView):

    url = r"^$"

    def get(self, *args, **kwrags):

        return self.render_to_response({})


class AddView(BaseView):

    def post(self, *args, **kwrags):

        song_id = self.request.POST.get("song_id")
        try:
            SongService().add_song(song_id)
        except Exception, e:
            return self.json_response({"error": str(e)})

        return self.response("ok")


class DeleteView(BaseView):

    def post(self, *args, **kwrags):

        song_id = self.request.POST.get("song_id")
        try:
            SongService().delete_song(song_id)
        except Exception, e:
            return self.json_response({"error": str(e)})

        return self.response("ok")


class PlayingListView(BaseView):

    def get(self, *args, **kwargs):

        playlist = PlayList.objects.get(id=1)
        qs = [x.song for x in PlayListSong.objects.filter(playlist=playlist)]

        columnIndexNameMap = {
            0: lambda song: self.render("playlist/song_stream.html", {"song": song, "playlist": playlist }),
            1: 'album',
            2: 'artist',
            3: lambda song: self.render("playlist/actions.html", {"song": song, "playlist": playlist })
        }
        sortIndexNameMap = {
            0: 'name' ,
            1: 'album' ,
            2: 'artist' ,
            3: None,
        }

        return SongService().open_search(self.request, columnIndexNameMap, sortIndexNameMap, qs=qs)


class CurrentSongView(BaseView):

    def get(self, *args, **kwrags):

        playlist = PlayList.objects.get(id=1)
        return self.render_to_response({"playlist": playlist, "player": SongService().player})


class MoveSongView(BaseView):

    def post(self, *args, **kwrags):

        song_id = self.request.POST.get("song_id")
        direction = self.request.POST.get("direction")

        try:
            SongService().move_song(song_id, direction)
        except Exception, e:
            return self.json_response({"error": str(e)})

        return self.response("ok")


class BulkMoveSongView(BaseView):

    def post(self, *args, **kwrags):

        data = self.request.POST.get("data")
        SongService().bulk_move_songs(data)

        return self.response("ok")


class SetVolumeView(BaseView):

    def post(self, *args, **kwrags):

        volume = self.request.POST.get("volume")
        SongService().player.change_volume(volume)

        return self.response("ok")


class SetPositionView(BaseView):

    def post(self, *args, **kwrags):

        position = int(self.request.POST.get("position", 0))
        SongService().player.seek(position)

        return self.response("ok")