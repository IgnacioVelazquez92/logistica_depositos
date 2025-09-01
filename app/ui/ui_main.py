# app/ui/ui_main.py
import tkinter as tk
from tkinter import ttk
from app.ui.ui_import import ImportFrame
from app.ui.ui_expiries import ExpiryFrame
from app.ui.ui_masters import MastersFrame


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Logística App")
        self.geometry("1100x650")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        nb.add(ImportFrame(nb), text="Importar")
        nb.add(ExpiryFrame(nb), text="Vencimientos")
        nb.add(MastersFrame(nb), text="Maestros")
