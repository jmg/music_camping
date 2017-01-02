SERVER_URL = "http://localhost:8000"
SERVER_URL = "http://live.devcloudsoftware.com"
UPDATE_INTERVAL = 0.5
NETWORK_TRIES = 3

try:
    from config_local import *
except:
    pass