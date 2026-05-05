import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

from app.models.domain import Region, Warehouse


class FixtureWarehouse(BaseModel):
    id: str
    name: str
    region: str


class FixtureInventoryRecord(BaseModel):
    warehouseId: str
    sku: str
    quantity: int


class FixturePayload(BaseModel):
    warehouses: list[FixtureWarehouse]
    inventory: list[FixtureInventoryRecord]


class FixtureRepository:
    def __init__(self, data_path: Path | None = None) -> None:
        if data_path is None:
            data_path = Path(__file__).resolve().parents[2] / "data" / "fixtures.json"
        self.data_path = data_path
        warehouse_data = FixturePayload.model_validate(self._load_warehouse_data())

        self._warehouses_data = {}
        for warehouse in warehouse_data.warehouses:
            self._warehouses_data[warehouse.id] = Warehouse(
                    id=warehouse.id,
                    name=warehouse.name,
                    region=Region(warehouse.region),
                )

        self._inventory_data = {}
        for record in warehouse_data.inventory:
            if record.warehouseId not in self._inventory_data.keys():
                self._inventory_data[record.warehouseId] = {}

            if record.sku not in self._inventory_data[record.warehouseId].keys():
                self._inventory_data[record.warehouseId][record.sku] = record.quantity
            else:
                self._inventory_data[record.warehouseId][record.sku] += record.quantity

    def _load_warehouse_data(self) -> dict:
        with self.data_path.open("r", encoding="utf-8") as fixture_file:
            return json.load(fixture_file)

    def all_warehouses(self) -> [Warehouse]:
        return list(self._warehouses_data.values())

    def warehouse_sku_count(self, warehouse_id: str, sku: str) -> int:
        if warehouse_id not in self._warehouses_data.keys() \
                or warehouse_id not in self._inventory_data.keys()\
                or sku not in self._inventory_data[warehouse_id].keys():
            return 0
        return self._inventory_data[warehouse_id][sku]

    def total_inventory_for(self, sku: str) -> int:
        total = 0
        for warehouse_id in self._inventory_data.keys():
            if sku in self._inventory_data[warehouse_id].keys():
                total = total + self._inventory_data[warehouse_id][sku]
        return total


@lru_cache
def get_repository() -> FixtureRepository:
    return FixtureRepository()
