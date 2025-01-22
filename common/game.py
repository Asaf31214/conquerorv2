import random
import uuid
from abc import ABC, abstractmethod

from typing_extensions import Dict, List, Optional, Tuple

from common.constants import *
from common.enums import *
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

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._amount >= other._amount


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
            ResourceType.FOOD: Food(INITIAL_FOOD),
            ResourceType.WOOD: Wood(INITIAL_WOOD),
            ResourceType.METAL: Metal(INITIAL_METAL),
        }
        self.controlled_tiles: List[Tile] = []
        self.unlocked_buildings: Dict[BuildingType, bool] = {
            BuildingType.HOUSE: True,
            BuildingType.MILITARY_CAMP: True,
            BuildingType.FARM: True,
            BuildingType.WOODCUTTER: False,
            BuildingType.MINE: False,
            BuildingType.BARRACK: True,
            BuildingType.STABLE: False,
            BuildingType.ARCHERY: False,
            BuildingType.DOCK: True,
        }

    def unlock_building(self, distance_to_capital: int):
        if distance_to_capital == 1:
            self.unlocked_buildings[BuildingType.WOODCUTTER] = True
            self.unlocked_buildings[BuildingType.STABLE] = True
        elif distance_to_capital == 2:
            self.unlocked_buildings[BuildingType.MINE] = True
            self.unlocked_buildings[BuildingType.ARCHERY] = True

    def add_resource(self, resource: Resource):
        self.resources[resource.resource_type] += resource

    def use_resource(self, resource: Resource):
        if self.resources[resource.resource_type] >= resource:
            self.resources[resource.resource_type] -= resource
            return True
        return False


class Unit(ABC):
    pass


class Worker(Unit):
    def __init__(self, faction: Faction):
        pass


class Soldier(Unit):
    def __init__(self, faction: Faction):
        pass

class Infantry(Soldier):
    pass

class Cavalry(Soldier):
    pass

class Archer(Soldier):
    pass


class Tile:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.type: Optional[TileType] = None
        self.shore = False
        self.max_hp: float = 0.0
        self.hp: float = 0.0
        self.faction: Optional[Faction] = None
        self.buildings: Optional[List[BuildingType]] = None
        self.soldiers: Optional[List[Unit]] = None
        self.treasure: Tuple[Food, Wood, Metal] = (Food(0), Wood(0), Metal(0))
        self.building_capacity = TILE_BUILDING_CAPACITY

    def get_rectangle(self):
        pass

    def change_faction(self, faction: Faction):
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

    def get_flattened_tiles(self):
        return [self.tiles[x][y] for y in range(self.height) for x in range(self.width)]

    def get_ocean_tiles(self) -> List[Tile]:
        vertical_center = ((self.height + 1) / 2) - 1
        horizontal_center = ((self.width + 1) / 2) - 1
        ocean_tiles = []
        for x in range(self.width):
            for y in range(self.height):
                if (
                    abs(x - horizontal_center) < OCEAN_WIDTH / 2
                    or abs(y - vertical_center) < OCEAN_WIDTH / 2
                ):
                    ocean_tiles.append(self.tiles[x][y])
        return ocean_tiles

    def get_shore_tiles(self) -> List[Tile]:
        shore_tiles = []
        for tile in self.get_flattened_tiles():
            shore = False
            for ocean_tile in self.get_ocean_tiles():
                if Board.get_relative_distance(tile, ocean_tile) == 1:
                    shore = True
                    break
            if shore:
                shore_tiles.append(tile)
        return [tile for tile in shore_tiles if tile not in self.get_ocean_tiles()]

    @staticmethod
    def get_relative_distance(tile_1: Tile, tile_2: Tile) -> int:
        x_diff = abs(tile_1.x - tile_2.x)
        y_diff = abs(tile_1.y - tile_2.y)
        return max(x_diff, y_diff)

    def place_environment(self):
        self.place_oceans()
        self.place_obstacles()
        self.place_bots()

    def place_oceans(self):
        for ocean_tile in self.get_ocean_tiles():
            ocean_tile.type = TileType.OCEAN

    def place_obstacles(self):
        for tile in self.get_flattened_tiles():
            allow_obstacle = True
            for corner_x, corner_y in self.corner_coordinates.values():
                distance = Board.get_relative_distance(
                    tile, self.tiles[corner_x][corner_y]
                )
                if distance <= 1:
                    allow_obstacle = False
            if allow_obstacle:
                if random.random() <= OBSTACLE_FREQUENCY:
                    tile.type = TileType.OBSTACLE

    def place_bots(self):
        for tile in self.get_flattened_tiles():
            if tile.type is None:
                pass # TODO


    def place_player(self, player: Player, corner: Corner):
        x, y = self.corner_coordinates[corner]
        capital = self.tiles[x][y]

        capital.type = TileType.LAND
        capital.max_hp = CAPITAL_HP
        capital.hp = capital.max_hp
        capital.faction = player.faction
        capital.buildings = None  # TODO
        capital.soldiers = None  # TODO
        capital.Treasure = (
            Food(CAPITAL_TREASURE),
            Wood(CAPITAL_TREASURE),
            Metal(CAPITAL_TREASURE),
        )

        player.faction.controlled_tiles.append(capital)


class Building(ABC):
    building_type: BuildingType
    resident_type: [Worker | Soldier]

    @abstractmethod
    def __init__(self, tile: Tile, capacity: int):
        self.tile = tile
        self.capacity = capacity
        self.residents: List[Unit] = []

    def have_space(self) -> bool:
        return len(self.residents) < self.capacity

    def add_resident(self, unit: Unit) -> None:
        if isinstance(unit, self.resident_type):
            self.residents.append(unit)
        else:
            raise TypeError(
            f"Cannot add {unit.__class__.__name__} to {self.building_type.value}"
            )


FARM_PRODUCTION_TYPE = Food
FARM_CONSUMPTION_TYPE = Wood
WOODCUTTER_PRODUCTION_TYPE = Wood
WOODCUTTER_CONSUMPTION_TYPE = Food
MINE_PRODUCTION_TYPE = Metal
MINE_CONSUMPTION_TYPE = Wood


class ProductionBuilding(Building):
    resident_type = Worker
    PRODUCTION_RATE: float
    PRODUCTION_TYPE: [Food | Wood | Metal]
    CONSUMPTION_RATE: float
    CONSUMPTION_TYPE: [Food | Wood | Metal]

    @abstractmethod
    def __init__(self, tile: Tile):
        super().__init__(tile, PRODUCTION_BUILDING_CAPACITY)

    def produce(self) -> bool:
        faction = self.tile.faction
        consumption = self.CONSUMPTION_TYPE(self.CONSUMPTION_RATE)
        if faction.use_resource(consumption):
            production = self.PRODUCTION_TYPE(self.PRODUCTION_RATE)
            faction.add_resource(production)
            return True
        return False


class Farm(ProductionBuilding):
    building_type = BuildingType.FARM
    PRODUCTION_RATE = FARM_PRODUCTION_RATE
    PRODUCTION_TYPE = FARM_PRODUCTION_TYPE
    CONSUMPTION_RATE = FARM_CONSUMPTION_RATE
    CONSUMPTION_TYPE = FARM_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class Woodcutter(ProductionBuilding):
    building_type = BuildingType.WOODCUTTER
    PRODUCTION_RATE = WOODCUTTER_PRODUCTION_RATE
    PRODUCTION_TYPE = WOODCUTTER_PRODUCTION_TYPE
    CONSUMPTION_RATE = WOODCUTTER_CONSUMPTION_RATE
    CONSUMPTION_TYPE = WOODCUTTER_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class Mine(ProductionBuilding):
    building_type = BuildingType.MINE
    PRODUCTION_RATE = MINE_PRODUCTION_RATE
    PRODUCTION_TYPE = MINE_PRODUCTION_TYPE
    CONSUMPTION_RATE = MINE_CONSUMPTION_RATE
    CONSUMPTION_TYPE = MINE_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class House(Building):
    building_type = BuildingType.HOUSE
    resident_type = Worker

    def __init__(self, tile: Tile):
        super().__init__(tile, HOUSE_CAPACITY)

    def create_worker(self, faction: Faction):
        worker = Worker(faction)
        self.add_resident(worker)

class MilitaryCamp(Building):
    building_type = BuildingType.MILITARY_CAMP
    resident_type = Soldier

    def __init__(self, tile: Tile):
        super().__init__(tile, MILITARY_CAMP_CAPACITY)