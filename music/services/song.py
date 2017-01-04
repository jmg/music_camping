from music.services.base import BaseService
#from music.services.player.connector import player
from music.services.playlist import PlayListService
from music.models import PlayList, Song, PlayListSong
import json
import threading
from django.core.cache import cache


class SongService(BaseService):

    entity = Song
    #player = player

    def play_song(self, song_id, callback=None):

        playlist = PlayListService().get_playlist()
        song = Song.objects.get(id=song_id)

        #self.player.stop()
        #self.player.play(song.path, callback=callback)

        playlist.current_song = song
        playlist.state = "Playing"
        playlist.save()

    def play_next_song(self, is_next=True, is_prev=False):

        playlist_song = self.change_song(is_next=is_next, is_prev=is_prev)
        self.play_song(playlist_song.song.id)

    def stop_song(self):

        playlist = PlayListService().get_playlist()

        #self.player.stop()

        playlist.state = "Not Playing"
        playlist.save()

    def pause_song(self):

        playlist = PlayListService().get_playlist()

        #self.player.pause()

        playlist.state = "Paused"
        playlist.save()

    def set_position(self, position):

        playlist = PlayListService().get_playlist()
        #self.player.seek(position)
        playlist.position_changed = True
        playlist.position = position
        playlist.save()

    def set_volume(self, volume):

        playlist = PlayListService().get_playlist()

        #self.player.change_volume(volume)

        playlist.volume = volume
        playlist.save()

    def get_player_data(self):

        playlist = PlayListService().get_playlist()
        try:
            return json.loads(cache.get("player_state_data"))
        except:
            return {}

    def change_song(self, is_next=True, is_prev=False):

        playlist = PlayListService().get_playlist()
        playlist_song = PlayListSong.objects.filter(song=playlist.current_song, playlist=playlist)[0]

        if is_next:
            songs = PlayListSong.objects.filter(playlist=playlist, sort__gt=playlist_song.sort).order_by("sort")
        elif is_prev:
            songs = PlayListSong.objects.filter(playlist=playlist, sort__lt=playlist_song.sort).order_by("-sort")

        if not songs:
            if is_next:
                sort = "sort"
            elif is_prev:
                sort = "-sort"
            songs = PlayListSong.objects.filter(playlist=playlist).order_by(sort)

        if not songs:
            raise Exception("No songs found")
        else:
            playlist_song = songs[0]

        playlist.current_song = playlist_song.song
        playlist.save()

        return playlist_song

    def add_song(self, song_id):

        song = Song.objects.get(id=song_id)

        playlist, created = PlayList.objects.get_or_create(id=1, defaults={"current_song": song})

        if created:
            playlist.save()

        if PlayListSong.objects.filter(song=song, playlist=playlist).count() > 0:
            raise Exception("Already on the playlist")

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

    def delete_song(self, song_id):

        playlist = PlayListService().get_playlist()

        song = Song.objects.get(id=song_id)

        playlist_song = PlayListSong.objects.get(song=song, playlist=playlist)
        playlist_song.delete()

    def move_song(self, song_id, direction):

        playlist = PlayListService().get_playlist()
        song = Song.objects.get(id=song_id)

        playlist_song = PlayListSong.objects.filter(song=song, playlist=playlist)
        if not playlist_song:
            raise Exception("song not found")

        playlist_song = playlist_song[0]

        if direction == "up":
            songs = PlayListSong.objects.exclude(id=playlist_song.id).filter(playlist=playlist, sort__lte=playlist_song.sort).order_by("-sort")

        elif direction == "down":
            songs = PlayListSong.objects.exclude(id=playlist_song.id).filter(playlist=playlist, sort__gte=playlist_song.sort).order_by("sort")

        if not songs:
            raise Exception("cannot move song")

        next_song = songs[0]

        current_sort = playlist_song.sort
        playlist_song.sort = next_song.sort
        next_song.sort = current_sort

        playlist_song.save()
        next_song.save()

    def bulk_move_songs(self, data):

        playlist = PlayListService().get_playlist()
        playlist_songs = [x for x in PlayListSong.objects.filter(playlist=playlist)]

        for song_data in json.loads(data):

            song = Song.objects.get(id=song_data["song_id"])
            playlist_song = PlayListSong.objects.filter(song=song, playlist=playlist)
            playlist_song = playlist_song[0]

            current_sort = playlist_song.sort
            playlist_song.sort = playlist_songs[song_data["new_position"]].sort

            playlist_song.save()

    def remove_media_songs(self):

        for song in SongService().filter(path__contains="/media/"):
            song.delete()