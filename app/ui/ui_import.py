# app/ui/ui_import.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from app.services.import_service import importar_excel
from app.dao.location_dao import list_locations

class ImportFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.path_var = tk.StringVar()
        self.resp_var = tk.StringVar(value="Sistema")

        tk.Label(self, text="Archivo Excel:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        tk.Entry(self, textvariable=self.path_var, width=60).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(self, text="Buscar...", command=self._pick).grid(row=0, column=2, padx=8, pady=8)

        tk.Label(self, text="Sucursal:").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        self.cmb_suc = ttk.Combobox(self, state="readonly", width=42)
        self.cmb_suc.grid(row=1, column=1, padx=8, pady=8, sticky="w")
        tk.Button(self, text="Actualizar sucursales", command=self._load_locations).grid(row=1, column=2, padx=8, pady=8)
        self._load_locations()

        tk.Label(self, text="Responsable (nombre):").grid(row=2, column=0, sticky="w", padx=8, pady=8)
        tk.Entry(self, textvariable=self.resp_var, width=40).grid(row=2, column=1, padx=8, pady=8, sticky="w")

        tk.Button(self, text="Importar", command=self._import).grid(row=3, column=1, padx=8, pady=16, sticky="w")

        # Escucha cambios de sucursales globales
        self.winfo_toplevel().bind("<<LocationsChanged>>", lambda e: self._load_locations())

    def _pick(self):
        p = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if p:
            self.path_var.set(p)

    def _load_locations(self):
        try:
            rows = list_locations()
            names = [r["nombre"] for r in rows]
            self.cmb_suc["values"] = names
            if not self.cmb_suc.get() and names:
                self.cmb_suc.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar sucursales: {e}")

    def _import(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("Atención", "Seleccioná un archivo Excel.")
            return

        sucursal_nombre = self.cmb_suc.get().strip()
        if not sucursal_nombre:
            messagebox.showwarning("Atención", "Elegí una sucursal del desplegable.")
            return

        responsable_nombre = self.resp_var.get().strip() or "Sistema"
        try:
            inv_id = importar_excel(
                path_excel=path,
                sucursal_nombre=sucursal_nombre,
                responsable_nombre=responsable_nombre,
            )
            messagebox.showinfo("Éxito", f"Inventario cargado con ID {inv_id}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
