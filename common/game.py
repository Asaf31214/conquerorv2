import uuid
from abc import ABC, abstractmethod

from typing_extensions import List, Optional, Tuple

from common.constants import *
from common.models import MakeMove


class Resource(ABC):
    resource_type: ResourceType

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
    resource_type = ResourceType.FOOD

    def __init__(self, amount: int):
        super().__init__(amount)


class Wood(Resource):
    resource_type = ResourceType.WOOD

    def __init__(self, amount: int):
        super().__init__(amount)


class Metal(Resource):
    resource_type = ResourceType.METAL

    def __init__(self, amount: int):
        super().__init__(amount)


class Faction:
    def __init__(self):
        self.resources = {
            ResourceType.FOOD: Food(0),
            ResourceType.WOOD: Wood(0),
            ResourceType.METAL: Metal(0),
        }
        self.controlled_tiles: List[Tile] = []

    def add_resource(self, resource: Resource):
        self.resources[resource.resource_type] += resource

    def use_resource(self, resource: Resource):
        if self.resources[resource.resource_type] >= resource:
            self.resources[resource.resource_type] -= resource
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
        self.type: Optional[TileType] = None
        self.max_hp: float = 0.0
        self.hp: float = 0.0
        self.faction: Optional[Faction] = None
        self.buildings: Optional[List[BuildingType]] = None
        self.units: Optional[List[Unit]] = None
        self.treasure: Tuple[Food, Wood, Metal] = (Food(0), Wood(0), Metal(0))

    def get_rectangle(self):
        pass


class Result:
    def to_dict(self) -> dict:
        pass


class Player:
    def __init__(self, faction: Faction, name: str):
        self.faction = faction
        self.id = f"player_{uuid.uuid4().hex}"
        self.name = name


class Game:
    def __init__(self, board_size: int):
        self.board = Board(board_size, board_size)
        self.players: List[Player] = []
        self.id = f"game_{uuid.uuid4().hex}"
        self.turn_queue: List[Player] = []
        self.started = False

    def add_player(self, player_name: str, corner: Corner) -> str:
        faction = Faction()
        player = Player(faction, player_name)
        self.board.place_player(player, corner)
        self.players.append(player)
        self.turn_queue.append(player)
        return player.id

    def get_player(self, player_id: str) -> Optional[Player]:
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def start(self):
        self.board.place_environment()
        self.started = True

    def make_move(self, move: MakeMove) -> Optional[Result]:
        player = self.get_player(move.player_id)
        if self.started and self.turn(player):
            pass
        return None

    def get_empty_corner(self) -> Optional[Corner]:
        for corner, occupation in self.board.corner_occupations.items():
            if not occupation:
                return corner
        return None

    def turn(self, player: Player):
        if self.turn_queue[0] == player:
            self.turn_queue = self.turn_queue[1:] + self.turn_queue[:1]
            return True
        return False

    def to_dict(self) -> dict:
        pass

    def __del__(self):
        pass


class Round:
    pass


class Move:
    pass


class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[List[Tile]] = [
            [Tile(x, y) for y in range(height)] for x in range(width)
        ]
        self.corner_occupations = {
            Corner.TOP_LEFT: False,
            Corner.TOP_RIGHT: False,
            Corner.BOTTOM_LEFT: False,
            Corner.BOTTOM_RIGHT: False,
        }
        self.corner_coordinates = {
            Corner.TOP_LEFT: (0, 0),
            Corner.TOP_RIGHT: (width - 1, 0),
            Corner.BOTTOM_LEFT: (0, height - 1),
            Corner.BOTTOM_RIGHT: (width - 1, height - 1),
        }

    def place_environment(self):
        self.place_oceans()
        self.place_obstacles()
        self.place_bots()

    def place_oceans(self):
        pass

    def place_obstacles(self):
        pass

    def place_bots(self):
        pass

    def place_player(self, player: Player, corner: Corner):
        x, y = self.corner_coordinates[corner]
        capital = self.tiles[x][y]

        capital.type = TileType.LAND
        capital.max_hp = CAPITAL_HP
        capital.hp = capital.max_hp
        capital.faction = player.faction
        capital.buildings = None  # TODO
        capital.units = None  # TODO
        capital.Treasure = (
            Food(CAPITAL_TREASURE),
            Wood(CAPITAL_TREASURE),
            Metal(CAPITAL_TREASURE),
        )

        player.faction.controlled_tiles.append(capital)


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
