from dataclasses import dataclass
from enum import Enum


class Region(str, Enum):
    NORTHEAST = "NORTHEAST"
    SOUTHEAST = "SOUTHEAST"
    MIDWEST = "MIDWEST"
    WEST = "WEST"
    SOUTHWEST = "SOUTHWEST"


class FulfillmentStatus(str, Enum):
    FULFILLED = "FULFILLED"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    UNFULFILLABLE = "UNFULFILLABLE"


class UnfulfillableReason(str, Enum):
    SKU_NOT_FOUND = "SKU_NOT_FOUND"
    INSUFFICIENT_INVENTORY = "INSUFFICIENT_INVENTORY"


@dataclass(frozen=True)
class Warehouse:
    id: str
    name: str
    region: Region
