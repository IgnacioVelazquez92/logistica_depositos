# app/ui/ui_main.py
import tkinter as tk
from tkinter import ttk

from app.ui.ui_import import ImportFrame
from app.ui.ui_expiries import ExpiryFrame
from app.ui.ui_masters import MastersFrame
from app.ui.ui_sales_import import SalesImportFrame  # <<< NUEVA PESTAÑA


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Logística - Vencimientos y Ventas")
        self.geometry("1200x700")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Tab: Importar recepciones/inventarios
        tab_import = ImportFrame(nb)
        nb.add(tab_import, text="Recepciones/Inventarios")

        # Tab: Importar ventas del mes (NUEVO)
        tab_sales = SalesImportFrame(nb)
        nb.add(tab_sales, text="Ventas (importar)")

        # Tab: Vencimientos (con ventas desde recepción)
        tab_exp = ExpiryFrame(nb)
        nb.add(tab_exp, text="Vencimientos")

        # Tab: Maestros (sucursales con ID)
        tab_master = MastersFrame(nb)
        nb.add(tab_master, text="Maestros")

        # Si tenés más:
        # tab_mov = MovementsFrame(nb); nb.add(tab_mov, text="Movimientos")
        # tab_stock = StockFrame(nb); nb.add(tab_stock, text="Stock")

def run():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    run()
