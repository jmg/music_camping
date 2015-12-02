from base import BaseView
from music.services.song import SongService
import os.path
from music.models import PlayList, Song


class PlayingView(BaseView):

    url = r"^playlist$"

    def get(self, *args, **kwrags):

        playlist = PlayList.objects.get(id=1)
        return self.render_to_response({"songs": playlist.songs.all()})


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


class SongListView(BaseView):

    def get(self, *args, **kwargs):

        columnIndexNameMap = { 0: 'name', 1: lambda song: self.render("playlist/actions.html", {"song": song}) }
        sortIndexNameMap = { 0: 'name' , 1: None, }

        return SongService().open_search(self.request, columnIndexNameMap, sortIndexNameMap)