# app/dao/connection.py
import sqlite3
from pathlib import Path
import os


def get_db_path() -> str:
    """
    Busca la ruta de la DB en .env (DB_PATH=...).
    Si no está definida, usa db/logistica.db.
    """
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
    """
    Ejecuta el schema.sql y crea las tablas si no existen.
    También precarga una sucursal y un responsable por defecto.
    """
    base = Path(__file__).resolve().parents[2]
    schema_path = base / "db" / "schema.sql"

    with get_conn() as conn, open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO locations(nombre, tipo) VALUES(?, ?)",
            ("Sucursal 1", "sucursal"),
        )
        cur.execute(
            "INSERT OR IGNORE INTO responsibles(nombre, contacto) VALUES(?, ?)",
            ("Sistema", ""),
        )
        conn.commit()
