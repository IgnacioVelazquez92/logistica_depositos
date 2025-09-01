# app/ui/ui_expiries.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.services.expiry_service import get_expiries
from app.dao.location_dao import list_locations

STATE_COLORS = {
    "CRITICO": "#ffdddd",
    "PROXIMO": "#fff3cd",
    "OK": "#ddffdd",
    "SIN_FECHA": "#e0e0e0"
}


class ExpiryFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.loc_id = tk.IntVar(value=0)
        self.query_var = tk.StringVar()
        self.show_expired_var = tk.BooleanVar(value=True)

        # Filtros
        top = tk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)

        tk.Label(top, text="Sucursal:").pack(side="left")
        self.cmb = ttk.Combobox(top, state="readonly", width=30)
        self.cmb.pack(side="left", padx=6)
        self._load_locations()

        tk.Label(
            top, text="Buscar (código/EAN/descripción):").pack(side="left", padx=10)
        tk.Entry(top, textvariable=self.query_var, width=32).pack(side="left")

        ttk.Checkbutton(top, text="Mostrar vencidos",
                        variable=self.show_expired_var).pack(side="left", padx=10)

        tk.Button(top, text="Actualizar", command=self.refresh).pack(
            side="left", padx=8)

        # Tabla
        cols = ("codigo", "descripcion", "ean", "fecha_venc",
                "dias_restantes", "cantidad", "estado", "ultima_carga")
        self.tree = ttk.Treeview(
            self, columns=cols, show="headings", height=20)
        headers = {
            "codigo": "Código",
            "descripcion": "Descripción",
            "ean": "EAN",
            "fecha_venc": "Vence",
            "dias_restantes": "Días",
            "cantidad": "Cant.",
            "estado": "Estado",
            "ultima_carga": "Última carga",
        }
        widths = {"codigo": 120, "descripcion": 300, "ean": 130, "fecha_venc": 110,
                  "dias_restantes": 80, "cantidad": 90, "estado": 110, "ultima_carga": 150}
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        for state, color in STATE_COLORS.items():
            self.tree.tag_configure(state, background=color)

        self.refresh()  # primera carga

    def _load_locations(self):
        try:
            locs = list_locations()
            names = ["(Todas)"] + [row["nombre"] for row in locs]
            ids = [0] + [row["id"] for row in locs]
        except Exception:
            names, ids = ["(Todas)"], [0]
        self.cmb["values"] = names
        self.cmb.current(0)
        self._loc_map = dict(zip(names, ids))
        self.cmb.bind("<<ComboboxSelected>>", lambda e: self._on_loc_change())

    def _on_loc_change(self):
        name = self.cmb.get()
        self.loc_id.set(self._loc_map.get(name, 0))

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        loc = self.loc_id.get() or None
        q = self.query_var.get().strip() or None
        include_expired = self.show_expired_var.get()
        try:
            rows = get_expiries(loc, q, include_expired)
        except Exception as e:
            self.tree.insert("", "end", values=(
                "", f"No se pudo cargar: {e}", "", "", "", "", "", ""))
            return

        for r in rows:
            iid = self.tree.insert("", "end", values=(
                r["codigo"], r["descripcion"], r["ean"],
                r["fecha_venc"], r["dias_restantes"],
                r["cantidad"], r["estado"], r.get("ultima_carga", "")
            ))
            self.tree.item(iid, tags=(r["estado"],))
