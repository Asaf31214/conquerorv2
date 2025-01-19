from enum import IntEnum, StrEnum


class ResourceType(IntEnum):
    FOOD = 0
    WOOD = 1
    METAL = 2


class BuildingType(StrEnum):
    FARM = "Farm"
    WOODCUTTER = "Woodcutter"
    MINE = "Mine"
    HOUSE = "House"
    BARRACK = "Barrack"
    STABLE = "Stable"


class UnitType(StrEnum):
    WORKER = "Worker"
    SOLDIER = "Soldier"
    HORSE = "Horse"


class MilitaryUnitType(StrEnum):
    INFANTRY = "Infantry"
    ARCHER = "Archer"
    CAVALRY = "Cavalry"


class BotType(StrEnum):
    WEAK = "Weak"
    MEDIUM = "Medium"
    STRONG = "Strong"


class TileType(StrEnum):
    LAND = "Land"
    OCEAN = "Ocean"
    OBSTACLE = "Obstacle"


class Corner(StrEnum):
    TOP_LEFT = "Top Left"
    TOP_RIGHT = "Top Right"
    BOTTOM_LEFT = "Bottom Left"
    BOTTOM_RIGHT = "Bottom Right"
