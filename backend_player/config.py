from os.path import expanduser
DEFAULT_SONGS_DIR = "%s/Music" % expanduser("~")

SERVER_URL = "http://live.devcloudsoftware.com"
UPDATE_INTERVAL = 0.5
NETWORK_TRIES = 3

BASE_DIR = expanduser("~")
DEFAULT_SONGS_DIR = "%s/Music" % BASE_DIR
DEFAULT_MEDIA_SONGS_DIR = BASE_DIR.replace("home", "media")

try:
    from config_local import *
except:
    pass