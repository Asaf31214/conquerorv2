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

player_name: str
request_manager: RequestManager
socket_manager: SocketManager
ui_manager: pygame_gui.UIManager
screen: pygame.Surface
ui_stage: UIStages
elements: List[UIElement] = []
element_actions: Dict[UIElement, Callable] = defaultdict(lambda: lambda **kwargs: None)
element_visibilities: Dict[UIStages, Dict[UIElement, bool]] = {
    UIStages.LOG_IN: defaultdict(bool),
    UIStages.MAIN_MENU: defaultdict(bool),
    UIStages.GAME_LOBBY: defaultdict(bool),
    UIStages.GAME_PLAYING: defaultdict(bool),
}


def set_stage(UIStage):
    global ui_stage
    ui_stage = UIStage
    update_visibilities()


def update_visibilities():
    current_stage_elements = element_visibilities[ui_stage]
    for element in elements:
        element.visible = current_stage_elements[element]


class WindowTile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x + TILE_OFFSET, y + TILE_OFFSET, TILE_INNER_SIZE, TILE_INNER_SIZE
        )
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
        self.tiles = [
            [WindowTile(x, y) for x in range(0, BOARD_SIZE, TILE_OUTER_SIZE)]
            for y in range(0, BOARD_SIZE, TILE_OUTER_SIZE)
        ]
        self.selected_tiles: List[Optional[WindowTile]] = [None, None]
        self.waiting_attack = False

    def update_selected_tile(self, pos):
        if tile := self.pos_to_tile(pos):
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


async def game_loop():
    clock = pygame.time.Clock()
    running = True
    last_event: Optional[pygame.event.Event] = None
    window_board = WindowBoard()

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            else:
                ui_manager.process_events(event)
                if (
                    event.type == pygame.USEREVENT
                    and last_event
                    and last_event.type == pygame.MOUSEBUTTONDOWN
                ):
                    await element_actions[event.ui_element](window_board=window_board)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    window_board.update_selected_tile(pos)

            last_event = event

        screen.fill(DARK_GRAY)
        window_board.draw()
        ui_manager.update(time_delta)
        ui_manager.draw_ui(screen)
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


async def log_in(**kwargs):
    global player_name
    input_field = [
        _ for _ in elements if _.most_specific_combined_id == "#player_name_input"
    ][0]
    assert isinstance(input_field, pygame_gui.elements.UITextEntryLine)
    player_name = input_field.get_text()
    set_stage(UIStages.MAIN_MENU)


def place_log_in_components():
    welcome_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, BOARD_SIZE), (250, 50)),
        text="Welcome to the Conqueror V2!",
        manager=ui_manager,
        object_id="#welcome_label",
    )

    player_name_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((0, BOARD_SIZE + 50), (250, 50)),
        manager=ui_manager,
        object_id="#player_name_input",
        placeholder_text="Enter your name",
    )
    player_name_input.unfocus()

    log_in_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, BOARD_SIZE + 100), (250, 50)),
        text="Log in",
        manager=ui_manager,
        object_id="#log_in_button",
    )

    element_visibilities[UIStages.LOG_IN][welcome_label] = True
    element_visibilities[UIStages.LOG_IN][player_name_input] = True
    element_visibilities[UIStages.LOG_IN][log_in_button] = True

    elements.append(welcome_label)
    elements.append(player_name_input)
    elements.append(log_in_button)

    element_actions[log_in_button] = log_in


def place_components():
    place_log_in_components()

    set_stage(UIStages.LOG_IN)


async def game_client():
    global request_manager, socket_manager, ui_manager, element_actions, screen, ui_stage
    load_dotenv()
    request_manager = RequestManager(API_URL)
    socket_manager = SocketManager(WS_URL)
    ui_stage = UIStages.LOG_IN
    pygame.init()
    ui_manager = pygame_gui.UIManager(WINDOW_SIZE)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    place_components()
    await game_loop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(game_client())
