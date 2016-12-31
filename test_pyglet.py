import gst
from multiprocessing import Process

def get_uri(path):
    if path.find("http://") != -1 or path.find("file://") != -1:
        return path
    return "file://" + path

def main():
    path = '/home/jmg/Music/Chunky.mp3'
    player = gst.element_factory_make("playbin", "player")
    time_format = gst.Format(gst.FORMAT_TIME)

    uri = get_uri(path)

    player.set_property('uri', uri)
    player.set_state(gst.STATE_PLAYING)

    import time
    time.sleep(10)

p = Process(target=main)
p.start()