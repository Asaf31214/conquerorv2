from abc import ABC, abstractmethod

from typing_extensions import List, Optional, Tuple

from common.constants import *
from common.models import MakeMove


class Resource(ABC):
    ResourceType: Resources

    @abstractmethod
    def __init__(self, amount: float):
        self._amount = amount

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._amount + other._amount)

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._amount - other._amount)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._amount == other._amount

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._amount < other._amount


class Food(Resource):
    ResourceType = Resources.FOOD

    def __init__(self, amount: int):
        super().__init__(amount)


class Wood(Resource):
    ResourceType = Resources.WOOD

    def __init__(self, amount: int):
        super().__init__(amount)


class Metal(Resource):
    ResourceType = Resources.METAL

    def __init__(self, amount: int):
        super().__init__(amount)


class Faction:
    def __init__(self):
        self._resources = {
            Resources.FOOD: Food(0),
            Resources.WOOD: Wood(0),
            Resources.METAL: Metal(0),
        }

    def get_resources(self, resource: Resources):
        return self._resources[resource]

    def add_resource(self, resource: Resource):
        self._resources[resource.ResourceType] += resource

    def use_resource(self, resource: Resource):
        if self._resources[resource.ResourceType] >= resource:
            self._resources[resource.ResourceType] -= resource
            return True
        return False


class Building:
    pass


class Unit:
    pass


class Tile:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.type: Optional[str] = None
        self.hp: float = 0.0
        self.max_hp: float = 0.0
        self.faction: Optional[Faction] = None
        self.buildings: Optional[List[Building]] = None
        self.units: Optional[List[Unit]] = None
        self.treasure: Tuple[Food, Wood, Metal] = (Food(0), Wood(0), Metal(0))

    def get_rectangle(self):
        pass


class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._tiles: List[List[Tile]] = [
            [Tile(x, y) for y in range(height)] for x in range(width)
        ]

    def get_tile(self, x: int, y: int):
        return self._tiles[x][y]

    def place_bots(self):
        pass

    def place_player(self):
        pass


class Result:
    def to_dict(self) -> dict:
        pass


class Game:
    def __init__(self, board_size: int):
        self.board = Board(board_size, board_size)

    def add_player(self, player_name) -> str:
        pass

    def make_move(self, move: MakeMove) -> Optional[Result]:
        pass

    def is_full(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass

    def __del__(self):
        pass


class Round:
    pass


class Move:
    pass


class Player:
    def __init__(self, team: Faction):
        self.team = team


class ProductionBuilding(ABC, Building):
    PRODUCTION_RATE: float
    PRODUCTION_TYPE: Resource
    CONSUMPTION_RATE: float
    CONSUMPTION_TYPE: Resource

    @abstractmethod
    def __init__(self, tile: Tile):
        self.tile = tile

    def produce(self) -> bool:
        faction = self.tile.faction
        consumption = ProductionBuilding.CONSUMPTION_TYPE.__init__(
            ProductionBuilding.CONSUMPTION_RATE
        )
        if faction.use_resource(consumption):
            production = ProductionBuilding.PRODUCTION_TYPE.__init__(
                ProductionBuilding.PRODUCTION_RATE
            )
            faction.add_resource(production)
            return True
        return False


class Farm(ProductionBuilding):
    PRODUCTION_RATE = FARM_PRODUCTION_RATE
    PRODUCTION_TYPE = FARM_PRODUCTION_TYPE
    CONSUMPTION_RATE = FARM_CONSUMPTION_RATE
    CONSUMPTION_TYPE = FARM_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class Woodcutter(ProductionBuilding):
    PRODUCTION_RATE = WOODCUTTER_PRODUCTION_RATE
    PRODUCTION_TYPE = WOODCUTTER_PRODUCTION_TYPE
    CONSUMPTION_RATE = WOODCUTTER_CONSUMPTION_RATE
    CONSUMPTION_TYPE = WOODCUTTER_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class Mine(ProductionBuilding):
    PRODUCTION_RATE = MINE_PRODUCTION_RATE
    PRODUCTION_TYPE = MINE_PRODUCTION_TYPE
    CONSUMPTION_RATE = MINE_CONSUMPTION_RATE
    CONSUMPTION_TYPE = MINE_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)
