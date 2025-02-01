import os
import httpx

class RequestManager:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.api_key = os.environ.get("API_KEY", "")

    async def get_game_list(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/games",
                headers={"x-api-key": self.api_key},
                timeout=10,
            )
            game_list = response.json()["games"]
            return game_list if game_list else ["No games found"]


class SocketManager:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
