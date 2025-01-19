from pydantic import BaseModel
from typing_extensions import Optional, Tuple


class CreateNewGameRequest(BaseModel):
    board_size: int


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
