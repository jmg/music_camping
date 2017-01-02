import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

import os
import time
import json
import requests
import config
import os
import eyed3
import threading
import random


class Player(object):

    def __init__(self):

        self.server_url = config.SERVER_URL
        self.sleep_time = config.UPDATE_INTERVAL
        self.network_tries = config.NETWORK_TRIES

        self.player = Gst.ElementFactory.make("playbin", "player")
        self.current_position = self.get_position(convert_time=False)
        self.current_song = None
        self.songs_list = []

    def play_forever(self):

        network_errors = 0

        while True:

            state_data = self.get_player_data()

            try:
                response = requests.post("%s/player/state/" % (self.server_url, ), data={"data": json.dumps(state_data) })
                data = response.json()
                network_errors = 0
            except:
                if network_errors < self.network_tries:
                    #keep trying until can reach the server
                    network_errors += 1
                    self.wait()
                    continue

                network_errors = 0

                if self.is_playing() and not self.song_finished():
                    self.wait()
                    continue

                #if max network_errors exceeded then shuffle playlist with local data
                data = self.get_local_data()
                if not data:
                    self.wait()
                    continue

            self.update_player(data)
            self.wait()

    def wait(self):

        time.sleep(self.sleep_time)

    def get_local_data(self):

        if not self.songs_list:
            self.songs_list.extend(self.list_songs_dir(config.DEFAULT_SONGS_DIR, analize_file=False))
            self.songs_list.extend(self.list_songs_dir(config.DEFAULT_MEDIA_SONGS_DIR, analize_file=False))

        if not self.songs_list:
            return

        song = random.choice(self.songs_list)

        data = {
            "path": song["path"],
            "state": "Playing",
        }

        return data

    def update_player(self, data):

        #print data

        if data["state"] == "Playing":
            if not self.is_playing() and data["path"]:
                self.play(data["path"])

            elif data["path"] != self.current_song and data["path"]:
                self.stop()
                self.play(data["path"])
                self.current_song = data["path"]

        elif data["state"] == "Paused":
            self.pause()

        elif data["state"] == "Not Playing":
            self.stop()

        if data.get("volume"):
            self.set_volume(int(data["volume"]))

        if data.get("position_changed"):
            self.seek(int(data["position"]))

        if data.get("songs_directory_changed"):
            self.save_songs(data["songs_directory"])

    def save_songs(self, songs_directory):

        def save_song_async():

            songs = self.list_songs_dir(songs_directory)
            songs_lists = self.chunks(songs, 50)
            for songs_list in songs_lists:
                response = requests.post("%s/player/savesongs/" % (self.server_url, ), data={"songs": json.dumps(songs_list) })

        thread = threading.Thread(target=save_song_async)
        thread.start()

    def song_finished(self):

        if not self.is_playing():
            return False

        new_position = self.get_position(convert_time=False)

        if self.current_position == new_position:
            return True

        self.current_position = new_position
        return False

    def get_player_data(self):

        return {
            "current_position": self.get_position(),
            "current_song_lenght": self.get_song_lenght(),
            "current_position_timestamp": self.get_position_timestamp(),
            "is_playing": self.is_playing(),
            "song_finished": self.song_finished(),
        }

    def play(self, path, callback=None):

        self.callback = callback
        uri = self.get_uri(path)

        self.player.set_property('uri', uri)
        try:
            self.player.set_state(Gst.State.PLAYING)
        except:
            pass

        if callback:
            bus = self.player.get_bus()
            bus.add_watch(self.event_listener)

    def get_uri(self, path):
        if path.find("http://") != -1 or path.find("file://") != -1:
            return path
        return "file://" + path

    def stop(self):
        if self.is_playing():
            self.player.set_state(Gst.State.NULL)

    def resume(self):
        if not self.is_playing():
            self.player.set_state(Gst.State.PLAYING)

    def pause(self):
        if self.is_playing():
            self.player.set_state(Gst.State.PAUSED)

    def get_position_timestamp(self):

        return self.get_position(convert_time=False)

    def get_position(self, convert_time=True):

        if self.is_playing():

            pos = None
            while not pos:
                try:
                    pos = self.player.query_position(Gst.Format.TIME)[1]
                except:
                    pass

            if convert_time:
                return self.convert_time(pos)
            return pos

        if convert_time:
            return "00:00"
        return 0

    def get_song_lenght(self):
        try:
            return self.player.query_duration(Gst.Format.TIME)[1]
        except:
            return 0

    def seek(self, position):

        self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, position)

    def set_volume(self, volume):

        self.player.set_property("volume", float(int(volume)/100.0))

    def get_volume(self):

        return self.player.get_property("volume") * 100

    def is_playing(self):

        self.state = self.player.get_state(0)[1]
        if self.state.value_nick == 'playing':
            return True
        return False

    def is_paused(self):

        self.state = self.player.get_state(0)[1]
        if self.state.value_nick == 'paused':
            return True
        return False

    def event_listener(self, bus, event):

        if event.type == gst.MESSAGE_EOS:
            #NOT WORKING (EVENT DONT FIRE)
            if self.callback:
                self.callback()

        return True

    def convert_time(self, time):
        time_int = time / 1000000000
        mins = time_int / 60
        segs = time_int % 60
        if mins < 10:
            mins = "0" + str(mins)
        else:
            mins = str(mins)

        if segs < 10:
            segs = "0" + str(segs)
        else:
            segs = str(segs)

        return mins + ":" + segs

    def list_songs_dir(self, songs_directory, analize_file=True):

        songs = []
        for directory, sub_folders, files in os.walk(songs_directory):
            for file in files:
                if self.valid_format(file):

                    path = os.path.join(directory, file)

                    if not analize_file:
                        songs.append({"path": path })
                        continue

                    audiofile = eyed3.load(path)

                    if audiofile is None:
                        continue

                    if audiofile.tag.title:
                        title = audiofile.tag.title
                    else:
                        try:
                            title = path.rsplit("/", 1)[-1]
                        except:
                            title = path

                    song = {
                        "path": path,
                        "title": title,
                        "artist": audiofile.tag.artist,
                        "album": audiofile.tag.album,
                    }

                    songs.append(song)

        return songs

    def valid_format(self, name):

        validFormats = ['.mp3','.wav','.wma', '.avi', '.ogg', '.flac']
        for format in validFormats:
            if name.find(format) != -1:
                return True
        return False

    def chunks(self, l, n):
        n = max(1, n)
        return (l[i:i+n] for i in xrange(0, len(l), n))


if __name__ == "__main__":
    Player().play_forever()