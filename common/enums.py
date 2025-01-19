from enum import IntEnum, StrEnum


class Resources(IntEnum):
    FOOD = 0
    WOOD = 1
    METAL = 2


class Buildings(StrEnum):
    FARM = "Farm"
    WOODCUTTER = "Woodcutter"
    MINE = "Mine"
    HOUSE = "House"
    BARRACK = "Barrack"
    STABLE = "Stable"


class Units(StrEnum):
    WORKER = "Worker"
    SOLDIER = "Soldier"
    HORSE = "Horse"


class MilitaryUnits(StrEnum):
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
