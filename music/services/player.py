import gst


class Player(object):

    def __init__(self):
        self.player = gst.element_factory_make("playbin", "player")
        self.time_format = gst.Format(gst.FORMAT_TIME)

    def play(self, path, next=None, id=None):
        self.next = next
        self.id = id

        uri = self.get_uri(path)

        self.player.set_property('uri', uri)
        try:
            self.player.set_state(gst.STATE_PLAYING)
        except:
            pass

        bus = self.player.get_bus()
        bus.add_watch(self.eventListener)

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

    def get_position(self):
        if self.is_playing():
            pos = None
            while not pos:
                try:
                    pos = self.player.query_position(self.time_format, None)[0]
                except:
                    pass
            return self.convert_time(pos)

        return "00:00"

    def get_seeked_position(self):
        if self.is_playing():
            pos = None
            while not pos:
                try:
                    pos = self.player.query_position(self.time_format, None)[0]
                except:
                    pass
            return pos

    def get_seekable_duration(self):
        return self.player.query_duration(gst.FORMAT_TIME, None)[0]

    def seek(self, position):
        self.player.seek(1.0, gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, position, gst.SEEK_TYPE_NONE,0)

    def change_volume(self, volume):
        self.player.set_property("volume",volume)

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

    def eventListener(self, bus, event):
        if event.type == gst.MESSAGE_EOS:
            self.next()
        return True

    #solucion no optima
    def songFinished(self):
        pos = self.getPosition()
        time.sleep(2)
        newPos = self.getPosition()
        if pos == newPos:
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