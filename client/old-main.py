import asyncio
import os

import httpx
import pygame
import pygame_gui
import websockets
from dotenv import load_dotenv

from client.config import *

API_KEY: str
running: bool
screen: pygame.Surface
game_id: str
ui_manager: pygame_gui.UIManager
text_display: pygame_gui.elements.UILabel


def set_api_key():
    load_dotenv()
    global API_KEY
    API_KEY = os.environ.get("API_KEY", "")


def initialize_game():
    global running, screen, ui_manager, text_display
    running = True
    pygame.init()
    screen = pygame.display.set_mode(MAIN_MENU_SCREEN_SIZE)
    pygame.display.set_caption(WINDOW_TITLE)

    ui_manager = pygame_gui.UIManager(MAIN_MENU_SCREEN_SIZE)
    text_display = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 10), (300, 50)),
        text="Welcome to game",
        manager=ui_manager,
    )


async def send_move_request(move_data):
    """Send a move to the server via an HTTP request asynchronously."""
    print(f"Move sent: {move_data}")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/demo_move",
            headers={"x-api-key": API_KEY},
            json={"x": move_data["x"], "y": move_data["y"], "game_id": game_id},
            timeout=10,
        )


async def listen_for_updates(game_id_: str):
    """Listen for updates from the WebSocket server."""
    socket_url = f"{WS_URL}/{Endpoints.WS.value}/{game_id_}"
    async with websockets.connect(socket_url) as ws:
        async for message in ws:
            print(f"Game update received: {message!r}")


async def create_game():
    url = f"{API_URL}/new_game"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={}, headers={"x-api-key": API_KEY})
        return response.json()["game_id"]


async def game_loop():
    global running
    clock = pygame.time.Clock()
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                move_data = {
                    "game_id": game_id,
                    "x": event.pos[0],
                    "y": event.pos[1],
                }
                asyncio.create_task(send_move_request(move_data))

            ui_manager.process_events(event)

        screen.fill((255, 255, 255))
        ui_manager.update(time_delta)
        ui_manager.draw_ui(screen)
        pygame.display.flip()
        await asyncio.sleep(0)


async def game():
    global game_id
    set_api_key()
    initialize_game()
    game_id = await create_game()
    asyncio.create_task(listen_for_updates(game_id))
    await game_loop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(game())
