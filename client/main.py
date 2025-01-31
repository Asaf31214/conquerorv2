import asyncio
from collections import defaultdict

import pygame
import pygame_gui
from dotenv import load_dotenv
from pygame_gui.core.ui_element import UIElement
from typing_extensions import Callable, Dict

from client.colors import *
from client.config import API_URL, TILE_SIZE, WINDOW_SIZE, WS_URL
from client.connection_manager import RequestManager, SocketManager

request_manager: RequestManager
socket_manager: SocketManager
ui_manager: pygame_gui.UIManager
screen: pygame.Surface
element_actions: Dict[UIElement, Callable] = defaultdict(lambda: lambda: None)


def dummy_action():
    print("Dummy action triggered")


async def game_loop():
    clock = pygame.time.Clock()
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                ui_manager.process_events(event)
                if event.type == pygame.USEREVENT:
                    element_actions[event.ui_element]()

        screen.fill(WHITE)
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
    hello_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((50, 50), (200, 50)),
        text="Say Hello",
        manager=ui_manager,
    )
    element_actions[hello_button] = dummy_action
    await game_loop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(game_client())
