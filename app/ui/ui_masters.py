# app/ui/ui_masters.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.dao.location_dao import ensure_location, list_locations, delete_location


class MastersFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # --- Alta de sucursales
        box = ttk.LabelFrame(self, text="Sucursales / Depósitos")
        box.pack(fill="x", padx=10, pady=10)

        ttk.Label(box, text="Nombre:").grid(
            row=0, column=0, padx=6, pady=6, sticky="w")
        self.nombre_var = tk.StringVar()
        ttk.Entry(box, textvariable=self.nombre_var, width=40).grid(
            row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Button(box, text="Agregar / Asegurar",
                   command=self._add_location).grid(row=0, column=2, padx=6, pady=6)

        # --- Listado + acciones
        lst_box = ttk.LabelFrame(self, text="Listado de sucursales")
        lst_box.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "nombre")
        self.tree = ttk.Treeview(
            lst_box, columns=cols, show="headings", height=10, selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.column("id", width=80, anchor="w")
        self.tree.column("nombre", width=320, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        btns = tk.Frame(self)
        btns.pack(pady=6)
        ttk.Button(btns, text="Actualizar listado",
                   command=self._refresh_list).pack(side="left", padx=6)
        ttk.Button(btns, text="Eliminar seleccionada",
                   command=self._delete_selected).pack(side="left", padx=6)

        self._refresh_list()

    def _add_location(self):
        nombre = (self.nombre_var.get() or "").strip()
        if not nombre:
            messagebox.showwarning(
                "Atención", "Ingresá un nombre de sucursal.")
            return
        try:
            ensure_location(nombre, "sucursal")
            messagebox.showinfo("OK", f"Sucursal '{nombre}' creada/asegurada.")
            self.nombre_var.set("")
            self._refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            for r in list_locations():
                self.tree.insert("", "end", iid=str(
                    r["id"]), values=(r["id"], r["nombre"]))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo listar sucursales: {e}")

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo(
                "Atención", "Seleccioná una sucursal en la tabla.")
            return
        loc_id = int(sel[0])
        nombre = self.tree.set(sel[0], "nombre")
        if not messagebox.askyesno("Confirmar", f"¿Eliminar la sucursal '{nombre}' (ID {loc_id})?"):
            return
        try:
            delete_location(loc_id)
            messagebox.showinfo("OK", f"Sucursal '{nombre}' eliminada.")
            self._refresh_list()
        except Exception as e:
            messagebox.showerror("No se pudo borrar", str(e))
