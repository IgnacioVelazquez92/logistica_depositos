# app/dao/connection.py
import sqlite3
from pathlib import Path

def get_db_path() -> str:
    base = Path(__file__).resolve().parents[2]
    env_path = base / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("DB_PATH"):
                return line.split("=", 1)[1].strip()
    return str(base / "db" / "logistica.db")

def get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    base = Path(__file__).resolve().parents[2]
    schema_path = base / "db" / "schema.sql"

    with get_conn() as conn, open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    with get_conn() as conn:
        cur = conn.cursor()
        # Seed NO intrusivo. Si está vacío, crea la sucursal 1 = Corrientes.
        cur.execute("SELECT COUNT(*) FROM locations")
        if (cur.fetchone()[0] or 0) == 0:
            cur.execute(
                "INSERT OR IGNORE INTO locations(id, nombre, tipo) VALUES(?, ?, ?)",
                (1, "Corrientes", "sucursal"),
            )
        cur.execute("SELECT COUNT(*) FROM responsibles")
        if (cur.fetchone()[0] or 0) == 0:
            cur.execute(
                "INSERT OR IGNORE INTO responsibles(nombre, contacto) VALUES(?, ?)",
                ("Sistema", ""),
            )
        conn.commit()
