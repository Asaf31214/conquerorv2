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
    FACTORY = "Factory"

    DOCK = "Dock"


class UnitType(StrEnum):
    WORKER = "Worker"
    SOLDIER = "Soldier"


class InfantryUnitType(StrEnum):
    SWORDSMAN = "Swordsman"
    SPEARMAN = "Spearman"
    ARCHER = "Archer"


class CavalryUnitType(StrEnum):
    LIGHT_CAVALRY = "Light Cavalry"
    HEAVY_CAVALRY = "Heavy Cavalry"
    HORSE_ARCHER = "Horse Archer"


class SiegeUnitType(StrEnum):
    CANNON = "Cannon"


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


class DefensiveBuildings(StrEnum):
    WALLS = "Walls"
    TOWER = "Tower"


class MoveTypes(StrEnum):
    ARMY = "Army"
    BUILD = "Build"
    CREATE = "Create"
    MODIFY = "Modify"
    TRANSFER = "Transfer"
