from enum import StrEnum

# API_URL = "https://conquerorv2-520018356558.europe-west1.run.app"
# WS_URL = "wss://conquerorv2-520018356558.europe-west1.run.app"
API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


TILE_INNER_SIZE = 45
TILE_OUTER_SIZE = 50
TILE_OFFSET = (TILE_OUTER_SIZE - TILE_INNER_SIZE) / 2
BOARD_SIZE = 600
MENU_SIZE = (600, 300)
WINDOW_SIZE = (MENU_SIZE[0], MENU_SIZE[1] + BOARD_SIZE)

WINDOW_TITLE = "Conqueror v2"


class Endpoints(StrEnum):
    WS = "ws"
