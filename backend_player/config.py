SERVER_URL = "http://live.devcloudsoftware.com"
UPDATE_INTERVAL = 0.5
NETWORK_TRIES = 3
DEFAULT_SONGS_DIR = "/home/pi/Music"

try:
    from config_local import *
except:
    pass