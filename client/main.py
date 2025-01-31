import asyncio
import os
from collections import defaultdict

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import pygame_gui
from dotenv import load_dotenv
from pygame_gui.core.ui_element import UIElement
from typing_extensions import Callable, Dict

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

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.selected:
            pygame.draw.rect(screen, RED, self.rect, 5)

class WindowBoard:
    def __init__(self, board_size: int):
        self.tiles = [[WindowTile(x, y)
                       for x in range(0, BOARD_SIZE, TILE_OUTER_SIZE)]
                      for y in range(0, BOARD_SIZE, TILE_OUTER_SIZE)]

    def draw(self):
        for row in self.tiles:
            for tile in row:
                tile.draw()


def dummy_action():
    print("Dummy action triggered")


async def game_loop():
    clock = pygame.time.Clock()
    running = True
    window_board = WindowBoard(BOARD_SIZE)
    selected_tile = None
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
                    for row in window_board.tiles:
                        for tile in row:
                            if tile.rect.collidepoint(pos):
                                if selected_tile:
                                    selected_tile.selected = False
                                selected_tile = tile
                                tile.selected = True

        screen.fill(WHITE)
        window_board.draw()
        ui_manager.update(time_delta)
        ui_manager.draw_ui(screen)
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


async def game_client():
    global request_manager, socket_manager, ui_manager, element_actions, screen
    load_dotenv()
    request_manager = RequestManager(API_URL)
    socket_manager = SocketManager(WS_URL)
    pygame.init()
    ui_manager = pygame_gui.UIManager(WINDOW_SIZE)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    hello_button = pygame_gui.elements.UIDropDownMenu(
        relative_rect=pygame.Rect((50, 50), (200, 50)),
        manager=ui_manager,
        starting_option="Hello",
        options_list=["Hello", "World"],
    )
    element_actions[hello_button] = dummy_action
    await game_loop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(game_client())
