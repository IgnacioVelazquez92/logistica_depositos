import tkinter as tk
from tkcalendar import DateEntry


class MovementsFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Fecha de vencimiento:").grid(
            row=0, column=0, padx=5, pady=5)
        self.fecha_venc = DateEntry(self, date_pattern="dd/mm/yyyy")
        self.fecha_venc.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        self.cantidad_entry = tk.Entry(self)
        self.cantidad_entry.grid(row=1, column=1, padx=5, pady=5)
