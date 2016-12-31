import gst
import time
import json
import requests
import config
import os


class Player(object):

    def __init__(self):

        self.server_url = config.SERVER_URL
        self.player = gst.element_factory_make("playbin", "player")
        self.time_format = gst.Format(gst.FORMAT_TIME)
        self.sleep_time = config.UPDATE_INTERVAL

        self.current_position = self.get_position(convert_time=False)

    def play_forever(self):

        while True:

            state_data = self.get_player_data()

            try:
                response = requests.post("%s/player/state/" % (self.server_url, ), data={"data": json.dumps(state_data) })
                data = response.json()
            except:
                print response.content
                time.sleep(self.sleep_time)
                continue

            print data

            if data["state"] == "Playing":
                if not self.is_playing() and data["path"]:
                    self.play(data["path"])

                elif data["song_changed"] and data["path"]:
                    self.stop()
                    self.play(data["path"])

            elif data["state"] == "Paused":
                self.pause()

            elif data["state"] == "Not Playing":
                self.stop()

            if data.get("volume"):
                self.set_volume(int(data["volume"]))

            if data["position_changed"]:
                self.seek(int(data["position"]))

            if data["songs_directory_changed"]:
                songs = self.list_songs_dir(data["songs_directory"])
                try:
                    response = requests.post("%s/player/savesongs/" % (self.server_url, ), data={"songs": json.dumps(songs) })
                    print response.status_code
                    open("file.html", "w").write(response.content)
                    print response.content
                except:
                    pass

            time.sleep(self.sleep_time)

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
            self.player.set_state(gst.STATE_PLAYING)
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
            self.player.set_state(gst.STATE_NULL)

    def resume(self):
        if not self.is_playing():
            self.player.set_state(gst.STATE_PLAYING)

    def pause(self):
        if self.is_playing():
            self.player.set_state(gst.STATE_PAUSED)

    def get_position_timestamp(self):

        return self.get_position(convert_time=False)

    def get_position(self, convert_time=True):

        if self.is_playing():

            pos = None
            while not pos:
                try:
                    pos = self.player.query_position(self.time_format, None)[0]
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
            return self.player.query_duration(self.time_format, None)[0]
        except:
            return 0

    def seek(self, position):

        self.player.seek(1.0, gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, position, gst.SEEK_TYPE_NONE,0)

    def set_volume(self, volume):

        self.player.set_property("volume", float(int(volume)/100.0))

    def get_volume(self):

        return self.player.get_property("volume") * 100

    def is_playing(self):

        self.state = self.player.get_state()[1]
        if self.state.value_nick == 'playing':
            return True
        return False

    def is_paused(self):

        self.state = self.player.get_state()[1]
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

    def list_songs_dir(self, songs_directory):

        songs = []
        for directory, sub_folders, files in os.walk(songs_directory):
            for file in files:
                if self.valid_format(file):
                    path = os.path.join(directory, file)
                    songs.append(path)

        return songs

    def valid_format(self, name):

        validFormats = ['.mp3','.wav','.wma', '.avi', '.ogg', '.flac']
        for format in validFormats:
            if name.find(format) != -1:
                return True
        return False


if __name__ == "__main__":
    Player().play_forever()