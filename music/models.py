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

    songs = models.ManyToManyField("Song", related_name="playlist_songs", through='PlayListSong')
    current_song = models.OneToOneField("Song", null=True, blank=True)

    state = models.CharField(max_length=50, null=True, blank=True)
    volume = models.CharField(max_length=50, null=True, blank=True)
    position = models.CharField(max_length=50, null=True, blank=True)

    position_changed = models.BooleanField(default=False)
    song_changed = models.BooleanField(default=False)

    def is_playing(self):

        return self.state == "Playing"


class Song(models.Model):

    path = models.CharField(max_length=2000)
    name = models.CharField(max_length=1000)
    artist = models.CharField(max_length=1000)
    genre = models.CharField(max_length=1000)
    album = models.CharField(max_length=1000)

    def get_streaming_url(self):

        return "http://localhost:8000/song/stream/?filename={0}".format(self.path)

    def to_json(self):

        return json.dumps({
            "id": self.id,
            "name": self.name,
            "uri": self.get_streaming_url(),
        })

    def __str__(self):

        return self.name


class PlayListSong(models.Model):

    song = models.ForeignKey("Song")
    playlist = models.ForeignKey("Playlist")
    sort = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ('sort',)

    def __str__(self):

        return "%s - %s" % (self.song.name, self.sort)



class UserProfile(models.Model):

    session_id = models.CharField(max_length=1000)
    submitted_songs = models.ManyToManyField("Song")