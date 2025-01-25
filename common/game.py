import random
import uuid
from abc import ABC, abstractmethod

from typing_extensions import Dict, List, Optional, Tuple, Type

from common.constants import *
from common.enums import *
from common.models import MakeMove


class Resource(ABC):
    resource_type: ResourceType

    @abstractmethod
    def __init__(self, amount: float):
        self._amount = amount

    def __add__(self, other):
        assert isinstance(other, self.__class__)
        return self.__class__(self._amount + other._amount)

    def __sub__(self, other):
        assert isinstance(other, self.__class__)
        return self.__class__(self._amount - other._amount)

    def __ge__(self, other):
        assert isinstance(other, self.__class__)
        return self._amount >= other._amount

    @staticmethod
    def objectify(costs: Tuple[float, float, float]):
        return {
            ResourceType.FOOD: Food(costs[0]),
            ResourceType.WOOD: Wood(costs[1]),
            ResourceType.METAL: Metal(costs[2]),
        }


class Food(Resource):
    resource_type = ResourceType.FOOD

    def __init__(self, amount: float):
        super().__init__(amount)


class Wood(Resource):
    resource_type = ResourceType.WOOD

    def __init__(self, amount: float):
        super().__init__(amount)


class Metal(Resource):
    resource_type = ResourceType.METAL

    def __init__(self, amount: float):
        super().__init__(amount)


class Faction:
    def __init__(self):
        self.resources = Resource.objectify(INITIAL_RESOURCES)
        self.controlled_tiles: List[Tile] = []
        self.unlocked_buildings: Dict[BuildingType, bool] = {
            BuildingType.HOUSE: True,
            BuildingType.MILITARY_CAMP: True,
            BuildingType.FARM: True,
            BuildingType.WOODCUTTER: False,
            BuildingType.MINE: False,
            BuildingType.BARRACK: True,
            BuildingType.STABLE: False,
            BuildingType.FACTORY: False,
            BuildingType.DOCK: True,
        }

    def unlock_building(self, distance_to_capital: int):
        if distance_to_capital == 1:
            self.unlocked_buildings[BuildingType.WOODCUTTER] = True
            self.unlocked_buildings[BuildingType.STABLE] = True
        elif distance_to_capital == 2:
            self.unlocked_buildings[BuildingType.MINE] = True
            self.unlocked_buildings[BuildingType.FACTORY] = True

    def add_resource(self, resource: Resource):
        self.resources[resource.resource_type] += resource

    def has_resource(self, resource: Resource) -> bool:
        return self.resources[resource.resource_type] >= resource

    def has_resources(self, resources: Dict[ResourceType, Resource]) -> bool:
        for resource_type, resource_amount in resources.items():
            if self.resources[resource_type] < resource_amount:
                return False
        return True

    def use_resource(self, resource: Resource):
        self.resources[resource.resource_type] -= resource

    def use_resources(self, resources: Dict[ResourceType, Resource]):
        for resource_type, resource_amount in resources.items():
            self.resources[resource_type] -= resource_amount


class Unit(ABC):
    unit_type: UnitType
    cost: Dict[ResourceType, Resource]

    @abstractmethod
    def get_properties(self) -> Dict:
        return {}


class Worker(Unit):
    unit_type = UnitType.WORKER
    cost = Resource.objectify(WORKER_COST)
    tool_cost = Resource.objectify(WORKER_TOOL_COST)

    def __init__(self):
        self.has_tool = False

    def equip_tool(self):
        self.has_tool = True

    def get_properties(self) -> Dict[str, bool]:
        return {"has_tool": self.has_tool}


class Soldier(Unit):
    unit_type = UnitType.SOLDIER
    soldier_type: InfantryUnitType | CavalryUnitType | SiegeUnitType
    unsheltered_round_cost = Resource.objectify(SOLDIER_UNSHELTERED_ROUND_COST)
    transport_round_cost = Resource.objectify(SOLDIER_TRANSPORT_ROUND_COST)

    @abstractmethod
    def __init__(self):
        self.is_sheltered = False
        self.is_transport = False

    def calculate_round_cost(self) -> Dict[ResourceType, Resource]:
        total_cost = {
            ResourceType.FOOD: Food(0),
            ResourceType.WOOD: Wood(0),
            ResourceType.METAL: Metal(0),
        }

        if not self.is_sheltered:
            for resource_type, cost in Soldier.unsheltered_round_cost.items():
                total_cost[resource_type] += cost

        if self.is_transport:
            for resource_type, cost in Soldier.transport_round_cost.items():
                total_cost[resource_type] += cost

        return total_cost

    def get_properties(
        self,
    ) -> Dict[str, InfantryUnitType | CavalryUnitType | SiegeUnitType]:
        return {"soldier_type": self.soldier_type}


class Swordsman(Soldier):
    soldier_type = InfantryUnitType.SWORDSMAN
    cost = Resource.objectify(SWORDSMAN_COST)

    def __init__(self):
        super().__init__()


class Spearman(Soldier):
    soldier_type = InfantryUnitType.SPEARMAN
    cost = Resource.objectify(SPEARMAN_COST)

    def __init__(self):
        super().__init__()


class Archer(Soldier):
    soldier_type = InfantryUnitType.ARCHER
    cost = Resource.objectify(ARCHER_COST)

    def __init__(self):
        super().__init__()


class LightCavalry(Soldier):
    soldier_type = CavalryUnitType.LIGHT_CAVALRY
    cost = Resource.objectify(LIGHT_CAVALRY_COST)

    def __init__(self):
        super().__init__()


class HeavyCavalry(Soldier):
    soldier_type = CavalryUnitType.HEAVY_CAVALRY
    cost = Resource.objectify(HEAVY_CAVALRY_COST)

    def __init__(self):
        super().__init__()


class HorseArcher(Soldier):
    soldier_type = CavalryUnitType.HORSE_ARCHER
    cost = Resource.objectify(HORSE_ARCHER_COST)

    def __init__(self):
        super().__init__()


class Cannon(Soldier):
    soldier_type = SiegeUnitType.CANNON
    cost = Resource.objectify(CANNON_COST)

    def __init__(self):
        super().__init__()


class Tile:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.type: Optional[TileType] = None
        self.shore = False
        self.max_hp: float = 0.0
        self.hp: float = 0.0
        self.faction: Optional[Faction] = None
        self.buildings: List["Building"] = []
        self.soldiers: List[Unit] = []
        self.treasure: dict[ResourceType, Food | Wood | Metal] = {
            ResourceType.FOOD: Food(0),
            ResourceType.WOOD: Wood(0),
            ResourceType.METAL: Metal(0),
        }
        self.building_capacity = TILE_BUILDING_CAPACITY
        self.tower_count = 0
        self.wall_count = 0

    def build_walls(self):
        self.wall_count += 1

    def build_tower(self) -> bool:
        if not self.tower_count == MAX_TOWER_PER_TILE:
            self.tower_count += 1
            return True
        return False

    def get_wall_damage_modifier(self):
        return WALL_DAMAGE_MODIFIER**self.wall_count

    def get_tower_archery_power(self):
        return self.tower_count * ARCHERY_POWER_PER_TOWER

    def change_faction(self, faction: Faction):
        self.hp = self.max_hp
        self.faction = faction
        self.buildings = [
            building
            for building in self.buildings
            if building.building_type
            not in [
                BuildingType.BARRACK,
                BuildingType.STABLE,
                BuildingType.FACTORY,
                BuildingType.MILITARY_CAMP,
            ]
        ]
        self.soldiers = []
        self.wall_count = 0
        for building in self.buildings:
            if isinstance(building, ResidentialBuilding):
                building.residents = []

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
    def __init__(self, board_size: int, ocean_width: int):
        self.board = Board(board_size, board_size, ocean_width)
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
        if player:
            if self.started and self.turn(player):
                pass  # todo
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


class Round:
    pass


class Move:
    pass


class Board:
    def __init__(self, width: int, height: int, ocean_width: int):
        self.width = width
        self.height = height
        self.ocean_width = ocean_width
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
                    abs(x - horizontal_center) < self.ocean_width / 2
                    or abs(y - vertical_center) < self.ocean_width / 2
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
        self.place_corner_treasures()
        self.place_oceans()
        self.place_obstacles()
        self.place_bots()

    def place_corner_treasures(self):
        for x, y in self.corner_coordinates.values():
            tile = self.tiles[x][y]
            if tile.type is None:
                tile.type = TileType.LAND
                #todo

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
                level = self.get_bot_level(tile)
                tile.type = TileType.LAND
                tile.max_hp = BOT_HP
                tile.hp = tile.max_hp
                army_size = BOT_BASE_ARMY_SIZE * level
                army_composition = self.get_bot_army_composition(level)
                if army_composition:
                    for i in range(army_size):
                        soldier_class = army_composition[i % len(army_composition)]
                        tile.soldiers.append(soldier_class())
                tile.treasure = Resource.objectify((BOT_BASE_TREASURE[0] * level,
                                                    BOT_BASE_TREASURE[1] * level,
                                                    BOT_BASE_TREASURE[2] * level))
                tile.wall_count = max(0, level-2)


    def get_bot_level(self, tile: Tile) -> int:
        x, y = tile.x, tile.y
        x_level = min(x, self.width - 1 - x)
        y_level = min(y, self.height - 1 - y)
        return max(x_level, y_level)
    
    @staticmethod
    def get_bot_army_composition(level: int) -> List[Type[Unit]]:
        level_0: List[Type[Unit]] = []
        level_1 = level_0 + [Swordsman, LightCavalry]
        level_2 = level_1 + [Spearman, HeavyCavalry]
        level_3 = level_2 + [Archer, HorseArcher]

        levels = [level_0, level_1, level_2, level_3]
        return levels[level]

    def place_player(self, player: Player, corner: Corner):
        x, y = self.corner_coordinates[corner]
        capital = self.tiles[x][y]

        capital.type = TileType.LAND
        capital.max_hp = CAPITAL_HP
        capital.hp = capital.max_hp
        capital.faction = player.faction
        capital.buildings = [House(capital)]
        capital.soldiers = []
        capital.treasure = Resource.objectify(CAPITAL_TREASURE)
        capital.build_tower()
        capital.build_walls()
        player.faction.controlled_tiles.append(capital)


class Building(ABC):
    building_type: BuildingType

    @abstractmethod
    def __init__(self, tile: Tile):
        self.tile = tile


class ResidentialBuilding(Building):
    resident_type: Type[Unit]

    @abstractmethod
    def __init__(self, tile: Tile, capacity: int):
        self.capacity = capacity
        self.residents: List[Unit] = []
        super().__init__(tile)

    def have_space(self) -> bool:
        return len(self.residents) < self.capacity

    def add_resident(self, unit: Unit) -> None:
        assert isinstance(unit, self.resident_type)
        self.residents.append(unit)

    def remove_resident(self, unit_data: Dict) -> Optional[Unit]:
        for unit in self.residents:
            if unit.get_properties() == unit_data:
                self.residents.remove(unit)
                return unit
        return None


FARM_PRODUCTION_TYPE = Food
FARM_CONSUMPTION_TYPE = Wood
WOODCUTTER_PRODUCTION_TYPE = Wood
WOODCUTTER_CONSUMPTION_TYPE = Food
MINE_PRODUCTION_TYPE = Metal
MINE_CONSUMPTION_TYPE = Wood


class ProductionBuilding(ResidentialBuilding):
    resident_type = Worker
    production_rate: float
    production_type: Type[Food | Wood | Metal]
    consumption_rate: float
    consumption_type: Type[Food | Wood | Metal]

    @abstractmethod
    def __init__(self, tile: Tile):
        super().__init__(tile, PRODUCTION_BUILDING_WORKER_CAPACITY)

    def produce(self):
        faction = self.tile.faction
        if faction:
            for worker in self.residents:
                assert isinstance(worker, Worker)
                enhancer = 2 if worker.has_tool else 1
                consumption = self.consumption_type(self.consumption_rate * enhancer)
                if faction.has_resource(consumption):
                    faction.use_resource(consumption)
                    production = self.production_type(self.production_rate)
                    faction.add_resource(production)


class Farm(ProductionBuilding):
    building_type = BuildingType.FARM
    production_rate = FARM_PRODUCTION_RATE
    production_type = FARM_PRODUCTION_TYPE
    consumption_rate = FARM_CONSUMPTION_RATE
    consumption_type = FARM_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class Woodcutter(ProductionBuilding):
    building_type = BuildingType.WOODCUTTER
    production_rate = WOODCUTTER_PRODUCTION_RATE
    production_type = WOODCUTTER_PRODUCTION_TYPE
    consumption_rate = WOODCUTTER_CONSUMPTION_RATE
    consumption_type = WOODCUTTER_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class Mine(ProductionBuilding):
    building_type = BuildingType.MINE
    production_rate = MINE_PRODUCTION_RATE
    production_type = MINE_PRODUCTION_TYPE
    consumption_rate = MINE_CONSUMPTION_RATE
    consumption_type = MINE_CONSUMPTION_TYPE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class House(ResidentialBuilding):
    building_type = BuildingType.HOUSE
    resident_type = Worker

    def __init__(self, tile: Tile):
        super().__init__(tile, HOUSE_CAPACITY)

    def create_worker(self, faction: Faction):
        if faction.has_resources(Worker.cost):
            faction.use_resources(Worker.cost)
            worker = Worker()
            self.add_resident(worker)


class MilitaryCamp(ResidentialBuilding):
    building_type = BuildingType.MILITARY_CAMP
    resident_type = Soldier

    def __init__(self, tile: Tile):
        super().__init__(tile, MILITARY_CAMP_CAPACITY)


class MilitaryBuilding(Building):
    creatable_soldiers: Dict[
        InfantryUnitType | CavalryUnitType | SiegeUnitType,
        Type[
            Swordsman
            | Spearman
            | Archer
            | LightCavalry
            | HeavyCavalry
            | HorseArcher
            | Cannon
        ],
    ]

    @abstractmethod
    def __init__(self, tile: Tile):
        super().__init__(tile)

    def create_soldier(
        self,
        faction: Faction,
        soldier_type: InfantryUnitType | CavalryUnitType | SiegeUnitType,
    ):
        soldier_class = self.creatable_soldiers[soldier_type]
        if faction.has_resources(soldier_class.cost):
            faction.use_resources(soldier_class.cost)
            soldier = soldier_class()
            self.tile.soldiers.append(soldier)
            return True
        return False


class Barracks(MilitaryBuilding):
    building_type = BuildingType.BARRACK

    def __init__(self, tile: Tile):
        super().__init__(tile)


class Stable(MilitaryBuilding):
    building_type = BuildingType.STABLE

    def __init__(self, tile: Tile):
        super().__init__(tile)


class Factory(MilitaryBuilding):
    building_type = BuildingType.FACTORY

    def __init__(self, tile: Tile):
        super().__init__(tile)
