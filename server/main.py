import uuid

import uvicorn
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from typing_extensions import Dict

from common.game import Game
from common.models import *
from server.WebSocketManager import ConnectionManager

manager: ConnectionManager
games: Dict[str, Game]


async def startup():
    global manager, games
    manager = ConnectionManager()
    games = {}


async def shutdown():
    global manager, games
    await manager.cleanup()
    games.clear()


app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])


@app.post("/new_game")
async def create_new_game(request: CreateNewGameRequest):
    board_size = request.board_size

    game_id = str(uuid.uuid4())
    new_game = Game(board_size)
    games[game_id] = new_game
    return {"game_id": game_id}


@app.delete("/delete_game")
async def delete_game(game_id: str):
    if game_id in games:
        del games[game_id]
        return Response(content="Game deleted", status_code=200)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.post("/add_player")
async def add_player(request: AddPlayerRequest):
    game_id = request.game_id
    player_name = request.player_name
    if game_id in games:
        game = games[game_id]
        if not game.is_full():
            player_id = game.add_player(player_name)
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
            await manager.broadcast(result.to_dict())
            return Response(content="Move successful", status_code=200)
        else:
            return Response(content="Invalid move", status_code=400)
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.get("/reconnect")
async def reconnect(game_id: str):
    if game_id in games:
        game = games[game_id]
        return game.to_dict()
    else:
        return Response(content="Game with given id does not exist", status_code=400)


@app.websocket("/websocket/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
