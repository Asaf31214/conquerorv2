from enum import StrEnum


class ResourceType(StrEnum):
    FOOD = "Food"
    WOOD = "Wood"
    METAL = "Metal"


class BuildingType(StrEnum):
    HOUSE = "House"
    MILITARY_CAMP = "Military Camp"

    FARM = "Farm"
    WOODCUTTER = "Woodcutter"
    MINE = "Mine"

    BARRACK = "Barrack"
    STABLE = "Stable"
    ARCHERY = "Archery"

    DOCK = "Dock"


class UnitType(StrEnum):
    WORKER = "Worker"
    SOLDIER = "Soldier"


class MilitaryUnitType(StrEnum):
    INFANTRY = "Infantry"
    CAVALRY = "Cavalry"
    ARCHER = "Archer"


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
