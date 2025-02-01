import asyncio
import os
from collections import defaultdict

from common.game import Game

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import pygame_gui
from dotenv import load_dotenv
from pygame_gui.core.ui_element import UIElement
from typing_extensions import Callable, Dict, List, Optional

from client.colors import *
from client.config import *
from client.connection_manager import RequestManager, SocketManager

player_name: str = ""
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
current_game: Optional[Game] = None


def get_element_by_id(element_id: str):
    return [
        element
        for element in elements
        if element.most_specific_combined_id == element_id
    ][0]


def set_stage(UIStage):
    global ui_stage
    ui_stage = UIStage
    update_visibilities()


def update_visibilities():
    current_stage_elements = element_visibilities[ui_stage]
    for element in elements:
        if current_stage_elements[element]:
            element.visible = 1
            element.show()
        else:
            element.visible = 0
            element.hide()


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
                    element_actions[event.ui_element](window_board=window_board)

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


def log_in(**kwargs):
    global player_name
    input_field = get_element_by_id("#player_name_input")
    assert isinstance(input_field, pygame_gui.elements.UITextEntryLine)
    player_name = input_field.get_text()
    load_main_menu()


def load_main_menu():
    main_menu_label = get_element_by_id("#main_menu_label")
    assert isinstance(main_menu_label, pygame_gui.elements.UILabel)
    main_menu_label.set_text(
        f"Welcome {player_name}, please join a game or create a new one."
    )

    set_stage(UIStages.MAIN_MENU)
    asyncio.create_task(get_game_list())


async def get_game_list():
    game_list = await request_manager.get_game_list()
    game_browser = get_element_by_id("#game_browser")
    assert isinstance(game_browser, pygame_gui.elements.UIDropDownMenu)
    game_browser.add_options(game_list)


def join_existing_game(**kwargs):
    async def inner():
        global current_game
        game_browser = get_element_by_id("#game_browser")
        assert isinstance(game_browser, pygame_gui.elements.UIDropDownMenu)
        game_id = game_browser.selected_option[0]
        if not game_id == "Select Game":
            asyncio.create_task(socket_manager.connect_game_socket(game_id))
            await request_manager.join_game(player_name, game_id)
            current_game = await request_manager.get_game(game_id)
            if current_game:
                print(f"connected to a game: {game_id}")

    asyncio.gather(inner())


def create_new_game(**kwargs):
    async def inner():
        global current_game
        new_game_id = await request_manager.create_game()
        asyncio.create_task(socket_manager.connect_game_socket(new_game_id))
        await request_manager.join_game(new_game_id, player_name)
        current_game = await request_manager.get_game(new_game_id)
        if current_game:
            print(f"connected to a game: {new_game_id}")

    asyncio.gather(inner())


def place_log_in_elements():
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


def place_main_menu_components():
    main_menu_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, BOARD_SIZE), (600, 50)),
        text=f"Welcome {player_name}, please join a game or create a new one.",
        manager=ui_manager,
        object_id="#main_menu_label",
    )

    game_browser = pygame_gui.elements.UIDropDownMenu(
        relative_rect=pygame.Rect((0, BOARD_SIZE + 50), (200, 50)),
        options_list=["Select Game"],
        starting_option="Select Game",
        manager=ui_manager,
        object_id="#game_browser",
        visible=0,
    )
    join_game = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, BOARD_SIZE + 100), (200, 50)),
        text="Join",
        manager=ui_manager,
        object_id="#join",
    )
    create_game = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((400, BOARD_SIZE + 50), (200, 50)),
        text="Create Game",
        manager=ui_manager,
        object_id="#create_game",
    )

    element_visibilities[UIStages.MAIN_MENU][main_menu_label] = True
    element_visibilities[UIStages.MAIN_MENU][game_browser] = True
    element_visibilities[UIStages.MAIN_MENU][join_game] = True
    element_visibilities[UIStages.MAIN_MENU][create_game] = True

    elements.append(main_menu_label)
    elements.append(game_browser)
    elements.append(join_game)
    elements.append(create_game)

    element_actions[join_game] = join_existing_game
    element_actions[create_game] = create_new_game


def place_elements():
    place_log_in_elements()
    place_main_menu_components()
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
    place_elements()
    await game_loop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(game_client())
