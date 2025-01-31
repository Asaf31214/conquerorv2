import asyncio
import os
from collections import defaultdict

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import pygame_gui
from dotenv import load_dotenv
from pygame_gui.core.ui_element import UIElement
from typing_extensions import Callable, Dict, List, Optional

from client.colors import *
from client.config import *
from client.connection_manager import RequestManager, SocketManager

request_manager: RequestManager
socket_manager: SocketManager
ui_manager: pygame_gui.UIManager
screen: pygame.Surface
element_actions: Dict[UIElement, Callable] = defaultdict(lambda: lambda: None)

class WindowTile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x+TILE_OFFSET, y+TILE_OFFSET, TILE_INNER_SIZE, TILE_INNER_SIZE)
        self.color = GRAY
        self.selected = False
        self.attacked = False

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.selected:
            pygame.draw.rect(screen, GREEN, self.rect, 5)
        elif self.attacked:
            pygame.draw.rect(screen, RED, self.rect, 5)

class WindowBoard:
    def __init__(self):
        self.tiles = [[WindowTile(x, y)
                       for x in range(0, BOARD_SIZE, TILE_OUTER_SIZE)]
                      for y in range(0, BOARD_SIZE, TILE_OUTER_SIZE)]
        self.selected_tiles: List[Optional[WindowTile]] = [None, None]
        self.waiting_attack = False

    def update_selected_tile(self, pos):
        if tile:=self.pos_to_tile(pos):
            if not self.waiting_attack:
                if self.selected_tiles[0] == tile:
                    if self.selected_tiles[0]:
                        self.selected_tiles[0].selected = False
                        self.selected_tiles[0] = None
                else:
                    if self.selected_tiles[0]:
                        self.selected_tiles[0].selected = False
                    self.selected_tiles[0] = tile
                    self.selected_tiles[0].selected = True
            else:
                self.selected_tiles[1] = tile
                tile.attacked = True


    def pos_to_tile(self, pos):
        for row in self.tiles:
            for tile in row:
                if tile.rect.collidepoint(pos):
                    return tile
        return None


    def draw(self):
        for row in self.tiles:
            for tile in row:
                tile.draw()


def dummy_action():
    print("Dummy action triggered")


async def game_loop():
    clock = pygame.time.Clock()
    running = True
    window_board = WindowBoard()
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                ui_manager.process_events(event)
                if event.type == pygame.USEREVENT:
                    element_actions[event.ui_element]()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    window_board.update_selected_tile(pos)

        screen.fill(WHITE)
        window_board.draw()
        ui_manager.update(time_delta)
        ui_manager.draw_ui(screen)
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()

def place_components():
    hello_button = pygame_gui.elements.UIDropDownMenu(
        relative_rect=pygame.Rect((0, BOARD_SIZE), (200, 50)),
        manager=ui_manager,
        starting_option="Hello",
        options_list=["Hello", "World"],
    )
    element_actions[hello_button] = dummy_action

async def game_client():
    global request_manager, socket_manager, ui_manager, element_actions, screen
    load_dotenv()
    request_manager = RequestManager(API_URL)
    socket_manager = SocketManager(WS_URL)
    pygame.init()
    ui_manager = pygame_gui.UIManager(WINDOW_SIZE)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    place_components()
    await game_loop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(game_client())
