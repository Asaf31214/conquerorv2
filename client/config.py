from enum import StrEnum

# API_URL = "https://conquerorv2-520018356558.europe-west1.run.app"
# WS_URL = "wss://conquerorv2-520018356558.europe-west1.run.app"
API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

MAIN_MENU_SCREEN_SIZE = (600, 400)
TILE_SIZE = 60
GAME_MENU_SCREEN_SIZE = (600, 400)
WINDOW_TITLE = "Conqueror v2"


class Endpoints(StrEnum):
    WS = "ws"
