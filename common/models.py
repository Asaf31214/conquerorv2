from pydantic import BaseModel
from typing_extensions import Optional, Tuple

from common.constants import DEFAULT_BOARD_SIZE, DEFAULT_OCEAN_WIDTH


class CreateNewGameRequest(BaseModel):
    board_size: int = DEFAULT_BOARD_SIZE
    ocean_width: int = DEFAULT_OCEAN_WIDTH


class AddPlayerRequest(BaseModel):
    game_id: str
    player_name: str


class MakeMove(BaseModel):
    player_id: str
    first_tile: Tuple[int, int]
    second_tile: Optional[Tuple[int, int]]
    action_type: str
    amount: Optional[float]


class MakeMoveRequest(MakeMove):
    game_id: str


class DemoRequest(BaseModel):
    game_id: str
    x: int
    y: int


class StartGameRequest(BaseModel):
    game_id: str
