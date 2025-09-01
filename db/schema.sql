-- db/schema.sql  (REEMPLAZAR COMPLETO POR ESTE)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    tipo TEXT
);

CREATE TABLE IF NOT EXISTS responsibles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    contacto TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    descripcion TEXT,
    ean TEXT,
    UNIQUE(codigo, ean)
);

CREATE TABLE IF NOT EXISTS inventories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    observacion TEXT,
    fecha_creacion DATETIME NOT NULL,
    fecha_exportacion DATETIME NOT NULL,
    tipo TEXT,
    total_filas INTEGER,
    sucursal_id INTEGER REFERENCES locations(id),
    responsable_id INTEGER REFERENCES responsibles(id),
    archivo_hash TEXT,
    UNIQUE(nombre, fecha_creacion, fecha_exportacion)
);

CREATE TABLE IF NOT EXISTS inventory_rows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER REFERENCES inventories(id),
    item_id INTEGER REFERENCES items(id),
    unidades_por_bulto REAL,
    bultos REAL,
    cantidad REAL,
    cantidad_total REAL,
    fecha_vencimiento DATE,
    fecha_ingreso DATETIME
);

CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER REFERENCES items(id),
    location_id INTEGER REFERENCES locations(id),
    lote TEXT,
    fecha_venc DATE,
    cantidad REAL,
    UNIQUE(item_id, location_id, lote, fecha_venc)
);

CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT,
    item_id INTEGER REFERENCES items(id),
    location_id INTEGER REFERENCES locations(id),
    delta REAL,
    lote TEXT,
    fecha_venc DATE,
    origen TEXT
);

CREATE INDEX IF NOT EXISTS idx_stock_item_loc ON stock(item_id, location_id, fecha_venc);
CREATE INDEX IF NOT EXISTS idx_items_ean_codigo ON items(ean, codigo);

-- Índices útiles para lotes (MIN/MAX/ SUM por lote)
CREATE INDEX IF NOT EXISTS idx_movements_lote_ts
ON movements(item_id, location_id, fecha_venc, ts);

CREATE INDEX IF NOT EXISTS idx_movements_tipo
ON movements(tipo);

-- =========================
--  VENTAS [NUEVO]
-- =========================

CREATE TABLE IF NOT EXISTS sales_imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    fecha_import DATETIME DEFAULT CURRENT_TIMESTAMP,
    archivo_hash TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_id INTEGER REFERENCES sales_imports(id),
    location_id INTEGER REFERENCES locations(id),
    item_id INTEGER REFERENCES items(id),
    fecha DATE NOT NULL,
    cantidad REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sales_loc_item_fecha
    ON sales(location_id, item_id, fecha);
