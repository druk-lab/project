import os
import tkinter as tk
from tkinter import ttk

from database.connection import init_db
from ui.session1 import Session1Frame
from ui.session2 import Session2Frame
from ui.session3_products import Session3ProductsFrame
from ui.session3_orders import Session3OrdersFrame
from ui.session4_users import Session4UsersFrame
from ui.session5_promotions import Session5PromotionsFrame
from ui.session5_loyalty import Session5LoyaltyFrame

from ui.session1 import DataManager  # важно!


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Belle Croissant Lyonnais — Desktop App (Sessions 1–5)")
        self.geometry("1200x800")

        # менеджер данных — общий для всех вкладок
        self.data_manager = DataManager()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Session 1 — аналитика
        s1 = Session1Frame(notebook, self.data_manager)
        notebook.add(s1, text="Session 1 — Data")

        # Session 2 — аналитика и дизайн
        s2 = Session2Frame(notebook)
        notebook.add(s2, text="Session 2 — Design")

        # Session 3–5: отдельные вкладки
        s3p = Session3ProductsFrame(notebook)
        notebook.add(s3p, text="S3 — Products")

        s3o = Session3OrdersFrame(notebook)
        notebook.add(s3o, text="S3 — Orders")

        s4 = Session4UsersFrame(notebook)
        notebook.add(s4, text="S4 — Users")

        s5p = Session5PromotionsFrame(notebook)
        notebook.add(s5p, text="S5 — Promotions")

        s5l = Session5LoyaltyFrame(notebook)
        notebook.add(s5l, text="S5 — Loyalty")


if __name__ == "__main__":
    init_db()   # создаёт базу
    app = MainApp()
    app.mainloop()
