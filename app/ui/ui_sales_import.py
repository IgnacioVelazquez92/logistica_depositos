# app/ui/ui_sales_import.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

from app.services.sales_service import import_sales_from_excel
from app.utils.normalize import canonicalize_columns
from app.utils.dates import to_date

def _detectar_meses(path: str):
    try:
        df = pd.read_excel(path, dtype=str)
        df.columns = canonicalize_columns(df.columns)
        if "fecha" not in df.columns:
            return []
        fechas = df["fecha"].map(to_date)
        meses = sorted({(d.year, d.month) for d in fechas if d is not None})
        return meses
    except Exception:
        return []

class SalesImportFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.path_var = tk.StringVar()
        self.mes_var = tk.StringVar(value="(sin detectar)")
        self.multi_var = tk.BooleanVar(value=False)

        # --- Archivo
        tk.Label(self, text="Archivo Excel (ventas):").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        tk.Entry(self, textvariable=self.path_var, width=60).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(self, text="Buscar...", command=self._pick).grid(row=0, column=2, padx=8, pady=8)

        # --- Mes(es) detectado(s)
        tk.Label(self, text="Mes(es) detectado(s):").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        tk.Label(self, textvariable=self.mes_var, fg="#555").grid(row=1, column=1, sticky="w", padx=8, pady=4)

        # --- Opción multi-mes
        ttk.Checkbutton(self, text="Permitir múltiples meses (delete+insert por cada mes)", variable=self.multi_var).grid(
            row=2, column=1, sticky="w", padx=8, pady=4
        )

        # --- Botón Importar
        tk.Button(self, text="Importar ventas", command=self._import).grid(row=3, column=1, sticky="w", padx=8, pady=12)

        # --- Log
        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=4, column=0, columnspan=3, sticky="ew", padx=8, pady=(8,4))

        tk.Label(self, text="Estado:").grid(row=5, column=0, sticky="nw", padx=8, pady=4)
        self.txt = tk.Text(self, height=10, width=90, state="disabled")
        self.txt.grid(row=5, column=1, columnspan=2, sticky="nsew", padx=8, pady=4)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _pick(self):
        p = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if p:
            self.path_var.set(p)
            meses = _detectar_meses(p)
            if meses:
                self.mes_var.set(", ".join(f"{y}-{m:02d}" for y, m in meses))
            else:
                self.mes_var.set("(sin detectar)")

    def _log(self, msg: str):
        self.txt.configure(state="normal")
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def _import(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("Atención", "Seleccioná un archivo Excel.")
            return
        self._log(f"Iniciando importación: {path}")

        try:
            res = import_sales_from_excel(path, import_name=f"ventas-{self.mes_var.get()}", allow_multi_month=self.multi_var.get())
            if res.get("status") == "ok":
                months = res.get("months", [])
                meses_txt = ", ".join(f"{m['year']}-{m['month']:02d}" for m in months) if months else "(sin info)"
                self._log(f"OK: meses {meses_txt}, filas insertadas: {res['rows']}, import_id: {res['import_id']}")
                messagebox.showinfo("Éxito", f"Ventas importadas para: {meses_txt}\nFilas: {res['rows']}")
            elif res.get("status") == "skipped":
                self._log(f"Saltado: {res.get('reason')}")
                messagebox.showinfo("Aviso", f"Importación omitida: {res.get('reason')}")
            else:
                self._log(str(res))
        except Exception as e:
            self._log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))
