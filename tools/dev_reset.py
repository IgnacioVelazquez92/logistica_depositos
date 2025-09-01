# tools/dev_reset.py
# Limpieza de datos para desarrollo.
# Uso:
#   python tools/dev_reset.py --only-inventories
#   python tools/dev_reset.py --all
#   python tools/dev_reset.py --delete-inventory 35

from app.dao import stock_dao, movement_dao
from app.dao.connection import get_conn, init_db
import argparse
import sys
from pathlib import Path

# Asegurar path del proyecto
BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))


def clear_inventories_and_stock():
    """
    Elimina:
      - inventory_rows
      - movements
      - inventories
      - stock
    Deja: locations, responsibles, items (para no perder maestros).
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM inventory_rows")
        cur.execute("DELETE FROM movements")
        cur.execute("DELETE FROM inventories")
        cur.execute("DELETE FROM stock")
        conn.commit()
    print("✔ Inventarios, filas, movimientos y stock eliminados (maestros conservados).")


def delete_inventory(inv_id: int):
    """
    Elimina una importación específica revirtiendo su impacto en stock.
    - Resta del stock cada 'cantidad_total' de esa importación.
    - Inserta movimientos de reversa.
    - Borra inventory_rows, movimientos del origen import:inv_id, y el inventory.
    """
    with get_conn() as conn:
        cur = conn.cursor()

        # Obtener sucursal del inventario
        cur.execute(
            "SELECT id, sucursal_id FROM inventories WHERE id=?", (inv_id,))
        inv = cur.fetchone()
        if not inv:
            print(f"✖ No existe inventario id={inv_id}")
            return
        sucursal_id = inv["sucursal_id"]

        # Traer filas del inventario
        cur.execute("""
            SELECT ir.item_id, ir.cantidad_total, ir.fecha_vencimiento
            FROM inventory_rows ir
            WHERE ir.inventory_id=?
        """, (inv_id,))
        rows = cur.fetchall()

        # Revertir stock y crear movimiento de reversa
        for r in rows:
            item_id = r["item_id"]
            delta = -float(r["cantidad_total"] or 0.0)
            fv = r["fecha_vencimiento"]
            # upsert negativo
            stock_dao.upsert_stock(item_id, sucursal_id, None, fv, delta)
            # movimiento de reversa
            movement_dao.insert_movement(
                tipo="reversa",
                item_id=item_id,
                location_id=sucursal_id,
                delta=delta,
                lote=None,
                fecha_venc=(fv if isinstance(fv, str)
                            or fv is None else str(fv)),
                origen=f"reversa:{inv_id}",
            )

        # Borrar movimientos de ese import
        cur.execute("DELETE FROM movements WHERE origen=?",
                    (f"import:{inv_id}",))
        # Borrar filas e inventario
        cur.execute(
            "DELETE FROM inventory_rows WHERE inventory_id=?", (inv_id,))
        cur.execute("DELETE FROM inventories WHERE id=?", (inv_id,))
        conn.commit()

    print(f"✔ Inventario {inv_id} eliminado y stock revertido.")


def reset_all():
    """
    Borra TODO y vuelve a crear el schema + seed (Sucursal 1, Sistema).
    Útil cuando querés arrancar de cero.
    """
    # Drop todas las tablas conocidas y recrear schema
    with get_conn() as conn:
        cur = conn.cursor()
        # Intento rápido de drop; si no existen, no pasa nada
        for t in ["inventory_rows", "movements", "stock", "inventories", "items", "responsibles", "locations"]:
            try:
                cur.execute(f"DROP TABLE IF EXISTS {t}")
            except Exception:
                pass
        conn.commit()

    # Recrear schema + seed
    init_db()
    print("✔ Base recreada y semillada (Sucursal 1 / Sistema).")


def main():
    ap = argparse.ArgumentParser(
        description="Herramientas de limpieza para desarrollo")
    ap.add_argument("--only-inventories", action="store_true",
                    help="Elimina inventories, inventory_rows, movements y stock")
    ap.add_argument("--all", action="store_true",
                    help="Borra TODO y recrea schema + seed")
    ap.add_argument("--delete-inventory", type=int,
                    help="Elimina una importación por ID (revirtiendo stock)")

    args = ap.parse_args()

    if args.all:
        reset_all()
        return

    if args.only_inventories:
        clear_inventories_and_stock()
        return

    if args.delete_inventory is not None:
        delete_inventory(args.delete_inventory)
        return

    ap.print_help()


if __name__ == "__main__":
    main()
