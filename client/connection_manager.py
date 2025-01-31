import os


class RequestManager:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.api_key = os.environ.get("API_KEY", "")


class SocketManager:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
