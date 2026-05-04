-- Order Routing Service — Schema and Seed Data
--
-- Compatible with SQLite, PostgreSQL, MySQL, and most SQL databases.
-- Adapt syntax as needed for your chosen database.

-- ============================================================
-- Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS warehouses (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    region      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    warehouse_id    TEXT NOT NULL,
    sku             TEXT NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (warehouse_id, sku),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
);

-- ============================================================
-- Warehouses
-- ============================================================

INSERT INTO warehouses (id, name, region) VALUES ('WH-EAST-1',    'Edison NJ Fulfillment Center',   'NORTHEAST');
INSERT INTO warehouses (id, name, region) VALUES ('WH-SOUTH-1',   'Atlanta GA Fulfillment Center',  'SOUTHEAST');
INSERT INTO warehouses (id, name, region) VALUES ('WH-MIDWEST-1', 'Columbus OH Fulfillment Center', 'MIDWEST');
INSERT INTO warehouses (id, name, region) VALUES ('WH-WEST-1',    'Reno NV Fulfillment Center',     'WEST');
INSERT INTO warehouses (id, name, region) VALUES ('WH-SOUTH-2',   'Dallas TX Fulfillment Center',   'SOUTHWEST');

-- ============================================================
-- Inventory
-- 10 SKUs distributed across warehouses with intentional
-- gaps and imbalances to create interesting routing scenarios.
-- ============================================================

-- SKU-WIDGET-BLUE: widely available
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-EAST-1',    'SKU-WIDGET-BLUE',   50);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-1',   'SKU-WIDGET-BLUE',   30);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-MIDWEST-1', 'SKU-WIDGET-BLUE',   20);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-WEST-1',    'SKU-WIDGET-BLUE',   15);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-2',   'SKU-WIDGET-BLUE',   10);

-- SKU-WIDGET-RED: concentrated in a few warehouses
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-EAST-1',    'SKU-WIDGET-RED',    5);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-1',   'SKU-WIDGET-RED',    40);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-MIDWEST-1', 'SKU-WIDGET-RED',    2);

-- SKU-GADGET-RED: only in West and Southwest
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-WEST-1',    'SKU-GADGET-RED',    25);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-2',   'SKU-GADGET-RED',    18);

-- SKU-GADGET-GREEN: available everywhere but low stock
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-EAST-1',    'SKU-GADGET-GREEN',  3);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-1',   'SKU-GADGET-GREEN',  4);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-MIDWEST-1', 'SKU-GADGET-GREEN',  2);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-WEST-1',    'SKU-GADGET-GREEN',  5);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-2',   'SKU-GADGET-GREEN',  1);

-- SKU-GIZMO-SILVER: only in one warehouse (forces single-source)
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-MIDWEST-1', 'SKU-GIZMO-SILVER',  60);

-- SKU-GIZMO-GOLD: scarce everywhere
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-EAST-1',    'SKU-GIZMO-GOLD',    1);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-1',   'SKU-GIZMO-GOLD',    2);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-WEST-1',    'SKU-GIZMO-GOLD',    1);

-- SKU-CABLE-USB-C: high volume, evenly distributed
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-EAST-1',    'SKU-CABLE-USB-C',   100);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-1',   'SKU-CABLE-USB-C',   100);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-MIDWEST-1', 'SKU-CABLE-USB-C',   100);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-WEST-1',    'SKU-CABLE-USB-C',   100);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-2',   'SKU-CABLE-USB-C',   100);

-- SKU-ADAPTER-HDMI: medium stock, absent from Southwest
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-EAST-1',    'SKU-ADAPTER-HDMI',  35);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-1',   'SKU-ADAPTER-HDMI',  20);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-MIDWEST-1', 'SKU-ADAPTER-HDMI',  15);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-WEST-1',    'SKU-ADAPTER-HDMI',  10);

-- SKU-BATTERY-AAA: only East and Midwest
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-EAST-1',    'SKU-BATTERY-AAA',   200);
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-MIDWEST-1', 'SKU-BATTERY-AAA',   150);

-- SKU-CHARGER-FAST: only Southwest with limited stock
INSERT INTO inventory (warehouse_id, sku, quantity) VALUES ('WH-SOUTH-2',   'SKU-CHARGER-FAST',  8);

