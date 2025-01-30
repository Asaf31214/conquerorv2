from enum import StrEnum

API_URL = "https://conquerorv2-520018356558.europe-west1.run.app"
WS_URL = "ws://conquerorv2-520018356558.europe-west1.run.app/ws"

MAIN_MENU_SCREEN_SIZE = (600, 400)
TILE_SIZE = 60
GAME_MENU_SCREEN_SIZE = (600, 400)
WINDOW_TITLE = "Conqueror v2"


class Endpoints(StrEnum):
    WS = "ws"
