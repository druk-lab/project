from tkinter import ttk, messagebox
import tkinter as tk
import requests

API_BASE = "http://127.0.0.1:5000"

class Session5PromotionsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()
        self.load_promotions()

    def _build_ui(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=10, pady=5)
        ttk.Button(top, text="Refresh", command=self.load_promotions).pack(side="left", padx=5)
        ttk.Button(top, text="Run Conflict Wizard (stub)", command=self.run_wizard).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self, columns=("id","name","type","value","start","end","priority"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        form = ttk.LabelFrame(self, text="Promotion")
        form.pack(fill="x", padx=10, pady=5)
        self.vars = {}
        for field in ["id","name","discount_type","discount_value","start_date","end_date","priority"]:
            row = ttk.Frame(form); row.pack(fill="x", pady=2)
            ttk.Label(row, text=field+":").pack(side="left", padx=5)
            v = tk.StringVar()
            self.vars[field] = v
            ttk.Entry(row, textvariable=v).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(form, text="Save", command=self.save_promotion).pack(padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_promotions(self):
        try:
            r = requests.get(f"{API_BASE}/api/promotions")
            data = r.json()
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=(row["id"], row["name"], row["discount_type"],
                                                row["discount_value"], row["start_date"], row["end_date"],
                                                row["priority"]))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        for k, v in zip(self.vars.keys(), vals):
            self.vars[k].set(v)

    def save_promotion(self):
        data = {
            "name": self.vars["name"].get(),
            "discount_type": self.vars["discount_type"].get() or "percent",
            "discount_value": float(self.vars["discount_value"].get() or 0),
            "start_date": self.vars["start_date"].get(),
            "end_date": self.vars["end_date"].get(),
            "priority": int(self.vars["priority"].get() or 1),
        }
        try:
            requests.post(f"{API_BASE}/api/promotions", json=data)
            self.load_promotions()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_wizard(self):
        messagebox.showinfo("Conflict Wizard",
                            "Здесь по заданию должен быть пошаговый мастер;\n"
                            "каркас есть, можно дописать SQL-проверки пересечения дат/продуктов.")
