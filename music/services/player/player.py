import gst
import time
from multiprocessing import Process

class Player(object):

    def __init__(self):

        self.player = gst.element_factory_make("playbin", "player")
        self.time_format = gst.Format(gst.FORMAT_TIME)

    def get_player_data(self):

        return {
            "current_position": self.get_position(),
            "current_song_lenght": self.get_song_lenght(),
            "current_position_timestamp": self.get_position_timestamp(),
            "is_playing": self.is_playing(),
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

    def change_volume(self, volume):

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

    #solucion no optima
    def song_finished(self):

        if not self.is_playing():
            time.sleep(1)
            return False

        current_pos = self.get_position(convert_time=False)
        time.sleep(1)
        new_position = self.get_position(convert_time=False)

        if current_pos == new_position:
            return True

        return False

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


player = Player()