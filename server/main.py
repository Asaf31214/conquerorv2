import asyncio
import os
import pickle

import uvicorn
from dotenv import load_dotenv
from fastapi import (Depends, FastAPI, HTTPException, Request, Response,
                     WebSocket, WebSocketDisconnect)
from typing_extensions import Dict

from common.game import Game
from common.models import *
from server.web_socket_manager import ConnectionManager

manager: ConnectionManager
games: Dict[str, Game]
API_KEY: str
ENVIRONMENT: str


async def startup():
    global manager, games, API_KEY, ENVIRONMENT
    manager = ConnectionManager()
    games = {}
    load_dotenv()
    API_KEY = os.environ.get("API_KEY", "")
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "")


async def shutdown():
    await manager.cleanup()
    games.clear()


async def require_api_key(request: Request):
    x_api_key = request.headers.get("x-api-key")
    if ENVIRONMENT == "cloud" and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


app = FastAPI(
    on_startup=[startup],
    on_shutdown=[shutdown],
)


@app.post("/new_game", dependencies=[Depends(require_api_key)])
async def create_new_game(request: CreateNewGameRequest):
    board_size = request.board_size
    ocean_width = request.ocean_width

    new_game = Game(board_size, ocean_width)
    game_id = new_game.id
    games[game_id] = new_game
    manager.active_connections[game_id] = []
    return {"game_id": game_id}


@app.post("/start_game", dependencies=[Depends(require_api_key)])
async def start_game(request: StartGameRequest):
    game_id = request.game_id
    if game_id in games:
        game = games[game_id]
        game.start()
        return Response(content="Game started", status_code=200)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.delete("/delete_game", dependencies=[Depends(require_api_key)])
async def delete_game(game_id: str):
    if game_id in games:
        del games[game_id]
        await manager.cleanup_game(game_id)
        return Response(content="Game deleted", status_code=200)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.post("/add_player", dependencies=[Depends(require_api_key)])
async def add_player(request: AddPlayerRequest):
    game_id = request.game_id
    player_name = request.player_name
    if game_id in games:
        game = games[game_id]
        if corner := game.get_empty_corner():
            player_id = game.add_player(player_name, corner)
            asyncio.create_task(
                manager.broadcast(
                    data={
                        "type": "join",
                        "details": {"player_name": player_name, "corner": corner},
                    },
                    game_id=game_id,
                )
            )
            return {"player_id": player_id}
        else:
            return Response(content="Game is already full", status_code=400)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.post("/make_move", dependencies=[Depends(require_api_key)])
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


@app.post("/demo_move", dependencies=[Depends(require_api_key)])
async def demo_move(request: DemoRequest):
    game_id = request.game_id
    x = request.x
    y = request.y
    if game_id in games:
        await manager.broadcast({"clicked_x": x, "clicked_y": y}, game_id)
        return Response(content="Move successful", status_code=200)
    return Response(content="Such game does not exist", status_code=400)


@app.get("/game_state", dependencies=[Depends(require_api_key)])
async def game_state(game_id: str):
    if game_id in games:
        game = games[game_id]
        return Response(
            content=pickle.dumps(game), media_type="application/octet-stream"
        )
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.get("/games", dependencies=[Depends(require_api_key)])
async def get_games():
    return {"games": list(games.keys())}


@app.get("/players", dependencies=[Depends(require_api_key)])
async def get_players(game_id: str):
    if game_id in games:
        game = games[game_id]
        return {"players": [player.id for player in game.players]}
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.websocket("/ws/{game_id}")
async def ws_game(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        await manager.disconnect(websocket, game_id)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
