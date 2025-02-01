import os
import pickle

from typing_extensions import List, Optional

from common.game import Game
import httpx
import websockets


class RequestManager:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.api_key = os.environ.get("API_KEY", "")

    async def get_game_list(self)->List[str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self.api_url}/games",
                headers={"x-api-key": self.api_key},
                timeout=60)
            return response.json()["games"]


    async def create_game(self)->str:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=f"{self.api_url}/new_game",
                                         headers={"x-api-key": self.api_key},
                                         json={},
                                         timeout=60)
            return response.json()["game_id"]

    async def join_game(self, game_id: str, player_name: str)-> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=f"{self.api_url}/add_player",
                                         headers={"x-api-key": self.api_key},
                                         json={"game_id": game_id, "player_name": player_name})
            return response.status_code == 200
        
    async def get_game(self, game_id: str) -> Optional[Game]:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=f"{self.api_url}/game_state?game_id={game_id}")
            if response.status_code == 200:
                game: Game = pickle.loads(response.content)
                return game



class SocketManager:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url

    async def connect_game_socket(self, game_id: str):
        socket_url = f"{self.ws_url}/ws/{game_id}"
        async with websockets.connect(socket_url) as ws:
            async for message in ws:
                print(f"Game update received: {message!r}")

