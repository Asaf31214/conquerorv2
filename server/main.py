import os

import uvicorn
from dotenv import load_dotenv
from fastapi import (Depends, FastAPI, HTTPException, Request, Response,
                     WebSocket, WebSocketDisconnect)
from typing_extensions import Dict

from common.game import Game
from common.models import *
from server.WebSocketManager import ConnectionManager

manager: ConnectionManager
games: Dict[str, Game]
API_KEY: str
ENVIRONMENT: str


async def startup():
    global manager, games, API_KEY, ENVIRONMENT
    manager = ConnectionManager()
    games = {}
    load_dotenv()
    API_KEY = os.environ.get("API_KEY")
    ENVIRONMENT = os.environ.get("ENVIRONMENT")


async def shutdown():
    global manager, games
    await manager.cleanup()
    games.clear()


async def require_api_key(request: Request):
    x_api_key = request.headers.get("x-api-key")
    if ENVIRONMENT == "cloud" and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


app = FastAPI(
    on_startup=[startup],
    on_shutdown=[shutdown],
    dependencies=[Depends(require_api_key)],
)


@app.post("/new_game")
async def create_new_game(request: CreateNewGameRequest):
    board_size = request.board_size

    new_game = Game(board_size)
    game_id = new_game.id
    games[game_id] = new_game
    return {"game_id": game_id}


@app.post("/start_game")
async def start_game(request: StartGameRequest):
    game_id = request.game_id
    if game_id in games:
        game = games[game_id]
        game.start()
        return Response(content="Game started", status_code=200)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.delete("/delete_game")
async def delete_game(game_id: str):
    if game_id in games:
        del games[game_id]
        await manager.cleanup_game(game_id)
        return Response(content="Game deleted", status_code=200)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.post("/add_player")
async def add_player(request: AddPlayerRequest):
    game_id = request.game_id
    player_name = request.player_name
    if game_id in games:
        game = games[game_id]
        if corner := game.get_empty_corner():
            player_id = game.add_player(player_name, corner)
            return {"player_id": player_id}
        else:
            return Response(content="Game is already full", status_code=400)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.post("/make_move")
async def make_move(request: MakeMoveRequest):
    game_id = request.game_id
    if game_id in games:
        game = games[game_id]
        move = MakeMove(**request.model_dump(exclude={"game_id"}))
        if result := game.make_move(move):
            await manager.broadcast(result.to_dict(), game_id)
            return Response(content="Move successful", status_code=200)
        else:
            return Response(content="Invalid move", status_code=400)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.get("/game_state")
async def game_state(game_id: str):
    if game_id in games:
        game = games[game_id]
        return game.to_dict()
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.get("/games")
async def games():
    return {"games": games.keys()}


@app.get("/players")
async def players(game_id: str):
    if game_id in games:
        game = games[game_id]
        return {"players": [player.id for player in game.players]}
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.websocket("/websocket/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        await manager.disconnect(websocket, game_id)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
