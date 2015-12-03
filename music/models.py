from django.db import models
import simplejson as json


class Config(models.Model):

    NETWORK_TYPES = (("Internet", "Internet"), ("Local", "Local"))
    network_type = models.CharField(max_length=20, choices=NETWORK_TYPES, default="Local")

    SONG_SELECTION_TYPES = (("Queue", "Queue"), ("Vote", "Vote"))
    song_selection_type = models.CharField(max_length=20, choices=SONG_SELECTION_TYPES, default="Queue")

    songs_limit = models.PositiveIntegerField()
    songs_limit_time = models.PositiveIntegerField()


class AdminUser(models.Model):

    pass


class PlayList(models.Model):

    songs = models.ManyToManyField("Song", related_name="playlist_songs")
    current_song = models.OneToOneField("Song", null=True, blank=True)


class Song(models.Model):

    path = models.CharField(max_length=2000)
    name = models.CharField(max_length=1000)
    artist = models.CharField(max_length=1000)
    genre = models.CharField(max_length=1000)

    def get_streaming_url(self):

        return "http://localhost:8000/song/stream/?filename={0}".format(self.path)

    def to_json(self):

        return json.dumps({
            "id": self.id,
            "name": self.name,
            "uri": self.get_streaming_url(),
        })


class UserProfile(models.Model):

    session_id = models.CharField(max_length=1000)
    submitted_songs = models.ManyToManyField("Song")