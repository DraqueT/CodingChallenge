from app.repositories.fixtures import FixtureRepository


def test_warehouse_count() -> None:
    repository = FixtureRepository()
    warehouses = repository.all_warehouses()
    assert len(warehouses) == 5


def test_sku_count() -> None:
    repository = FixtureRepository()
    assert repository.warehouse_sku_count("WH-EAST-1", "SKU-WIDGET-BLUE") == 50


def test_warehouse_sku_count() -> None:
    repository = FixtureRepository()
    assert repository.total_inventory_for("SKU-CHARGER-FAST") == 8


def test_sku_total_count() -> None:
    repository = FixtureRepository()
    assert repository.total_inventory_for("SKU-NOT-FOUND") == 0
