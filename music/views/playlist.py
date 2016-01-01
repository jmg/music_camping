from base import BaseView
from music.services.song import SongService
from music.services.player import player
import os.path
from music.models import PlayList, Song


class PlayingView(BaseView):

    url = r"^playlist$"

    def get(self, *args, **kwrags):

        playlist = PlayList.objects.get(id=1)
        return self.render_to_response({"playlist": playlist})


class ChangeSongView(BaseView):

    def post(self, *args, **kwrags):

        is_next = self.request.POST.get("next") is not None
        is_prev = self.request.POST.get("prev") is not None

        playlist = PlayList.objects.get(id=1)

        if is_next:
            songs = playlist.songs.filter(id__gt=playlist.current_song.id).order_by("id")[0:1]
        elif is_prev:
            songs = playlist.songs.filter(id__lt=playlist.current_song.id).order_by("-id")[0:1]

        if songs:
            song = songs[0]
        else:
            if is_next:
                songs = playlist.songs.order_by("id")
            elif is_prev:
                songs = playlist.songs.order_by("-id")

            if songs:
                song = songs[0]
            else:
                return self.json_response({"error": "No songs found"})

        playlist.current_song = song
        playlist.save()

        return self.response(song.to_json())


class PlayView(BaseView):

    def post(self, *args, **kwrags):

        song = Song.objects.get(id=self.request.POST.get("song_id"))
        player.stop()
        player.play(song.path)

        return self.response("ok")


class StopView(BaseView):

    def post(self, *args, **kwrags):

        player.stop()
        return self.response("ok")


class PauseView(BaseView):

    def post(self, *args, **kwrags):

        player.pause()
        return self.response("ok")


class SelectView(BaseView):

    url = r"^$"

    def get(self, *args, **kwrags):

        return self.render_to_response({})


class AddView(BaseView):

    def post(self, *args, **kwrags):

        song_id = self.request.POST.get("song_id")
        song = Song.objects.get(id=song_id)

        playlist, created = PlayList.objects.get_or_create(id=1, defaults={"current_song": song})

        if created:
            playlist.save()

        playlist.songs.add(song)
        playlist.save()

        return self.response("ok")


class DeleteView(BaseView):

    def post(self, *args, **kwrags):

        song_id = self.request.POST.get("song_id")
        song = Song.objects.get(id=song_id)
        song.delete()

        return self.response("ok")


class PlayingListView(BaseView):

    def get(self, *args, **kwargs):

        playlist = PlayList.objects.get(id=1)
        qs = playlist.songs.all()

        columnIndexNameMap = {
            0: lambda song: self.render("playlist/song_stream.html", {"song": song, "playlist": playlist }),
            1: lambda song: self.render("playlist/actions.html", {"song": song, "playlist": playlist })
        }
        sortIndexNameMap = { 0: 'name' , 1: None, }

        return SongService().open_search(self.request, columnIndexNameMap, sortIndexNameMap, qs=qs)