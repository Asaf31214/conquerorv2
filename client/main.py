import asyncio
import os

import httpx
import pygame
import websockets
from dotenv import load_dotenv

from client.config import *

API_KEY: str
running: bool
screen: pygame.Surface
game_id: str



def set_api_key():
    load_dotenv()
    global API_KEY
    API_KEY = os.environ.get("API_KEY", "")


def initialize_game():
    global running, screen
    running = True
    pygame.init()
    screen = pygame.display.set_mode(MAIN_MENU_SCREEN_SIZE)
    pygame.display.set_caption(WINDOW_TITLE)


async def send_move_request(move_data):
    """Send a move to the server via an HTTP request asynchronously."""
    async with httpx.AsyncClient() as client:
        print(f"Sending move")
        response = await client.post(
            f"{API_URL}/demo_move",
            headers={"x-api-key": API_KEY},
            json={"x": move_data["x"], "y": move_data["y"], "game_id": game_id},
            timeout=10,
        )
        print(f"Move sent: {move_data}, Response: {response.status_code}")


async def listen_for_updates(game_id_: str):
    """Listen for updates from the WebSocket server."""
    socket_url = f"{WS_URL}/{Endpoints.WS.value}/{game_id_}"
    async with websockets.connect(socket_url) as ws:
        async for message in ws:
            print(f"Game update received: {message}")


async def create_game():
    url = f"{API_URL}/new_game"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={})
        return response.json()["game_id"]


async def game_loop():
    global running
    while running:
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
        screen.fill((255, 255, 255))
        pygame.display.flip()
        await asyncio.sleep(0.5)


async def main_():
    set_api_key()
    initialize_game()
    global game_id
    game_id = await create_game()
    websocket_task = asyncio.create_task(listen_for_updates(game_id))
    await game_loop()
    websocket_task.cancel()


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
