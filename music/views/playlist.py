from base import BaseView
from music.services.song import SongService
from music.services.player import player
import os.path
from music.models import PlayList, Song, PlayListSong


class PlayingView(BaseView):

    url = r"^playlist$"

    def get(self, *args, **kwrags):

        playlist, _ = PlayList.objects.get_or_create(id=1)
        return self.render_to_response({"playlist": playlist, "player": player})


class ChangeSongView(BaseView):

    def post(self, *args, **kwrags):

        is_next = self.request.POST.get("next") is not None
        is_prev = self.request.POST.get("prev") is not None

        playlist, _ = PlayList.objects.get_or_create(id=1)

        if is_next:
            songs = playlist.songs.filter(id__gt=playlist.current_song.id).order_by("-sort")[0:1]
        elif is_prev:
            songs = playlist.songs.filter(id__lt=playlist.current_song.id).order_by("-sort")[0:1]

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

        playlist = PlayList.objects.get(id=1)
        song = Song.objects.get(id=self.request.POST.get("song_id"))

        player.stop()
        player.play(song.path)

        playlist.current_song = song
        playlist.save()

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

        if PlayListSong.objects.filter(song=song, playlist=playlist).count() > 0:
            return self.response("Already on the playlist")

        last_song = PlayListSong.objects.filter(playlist=playlist).order_by("-sort")
        if last_song:
            new_sort = last_song[0].sort + 1
        else:
            new_sort = 1

        PlayListSong(
            song=song,
            playlist=playlist,
            sort=new_sort,
        ).save()

        return self.response("ok")


class DeleteView(BaseView):

    def post(self, *args, **kwrags):

        playlist, created = PlayList.objects.get_or_create(id=1)
        song_id = self.request.POST.get("song_id")
        song = Song.objects.get(id=song_id)

        playlist_song = PlayListSong.objects.get(song=song, playlist=playlist)
        playlist_song.delete()

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
        return self.render_to_response({"playlist": playlist, "player": player})



class MoveSongView(BaseView):

    def post(self, *args, **kwrags):

        playlist = PlayList.objects.get(id=1)
        song = Song.objects.get(id=self.request.POST.get("song_id"))

        playlist_song = PlayListSong.objects.filter(song=song, playlist=playlist)
        if not playlist_song:
            return self.response("song not found")

        playlist_song = playlist_song[0]

        direction = self.request.POST.get("direction")
        if direction == "up":
            songs = PlayListSong.objects.exclude(id=playlist_song.id).filter(playlist=playlist, sort__lte=playlist_song.sort).order_by("-sort")

        elif direction == "down":
            songs = PlayListSong.objects.exclude(id=playlist_song.id).filter(playlist=playlist, sort__gte=playlist_song.sort).order_by("sort")

        if not songs:
            return self.response("cannot move song")

        next_song = songs[0]

        current_sort = playlist_song.sort
        playlist_song.sort = next_song.sort
        next_song.sort = current_sort

        playlist_song.save()
        next_song.save()

        return self.response("ok")

