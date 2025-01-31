from enum import StrEnum

# API_URL = "https://conquerorv2-520018356558.europe-west1.run.app"
# WS_URL = "wss://conquerorv2-520018356558.europe-west1.run.app"
API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


TILE_SIZE = 50
MENU_SIZE = (600, 400)
WINDOW_SIZE = (600, 1000)

WINDOW_TITLE = "Conqueror v2"


class Endpoints(StrEnum):
    WS = "ws"
