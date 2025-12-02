from tkinter import ttk, messagebox
import tkinter as tk
import requests

API_BASE = "http://127.0.0.1:5000"

class Session5LoyaltyFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        row = ttk.Frame(self); row.pack(fill="x", padx=10, pady=5)
        ttk.Label(row, text="Customer ID:").pack(side="left", padx=5)
        self.customer_id = tk.StringVar()
        ttk.Entry(row, textvariable=self.customer_id).pack(side="left", padx=5)
        ttk.Button(row, text="Load", command=self.load_points).pack(side="left", padx=5)

        row2 = ttk.Frame(self); row2.pack(fill="x", padx=10, pady=5)
        ttk.Label(row2, text="Points:").pack(side="left", padx=5)
        self.points = tk.StringVar()
        ttk.Entry(row2, textvariable=self.points).pack(side="left", padx=5)
        ttk.Button(row2, text="Save", command=self.save_points).pack(side="left", padx=5)

    def load_points(self):
        cid = self.customer_id.get()
        try:
            r = requests.get(f"{API_BASE}/api/loyalty/{cid}")
            if r.ok:
                self.points.set(str(r.json().get("points", 0)))
            else:
                messagebox.showerror("Error", r.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_points(self):
        cid = self.customer_id.get()
        pts = int(self.points.get() or 0)
        try:
            r = requests.put(f"{API_BASE}/api/loyalty/{cid}", json={"points": pts})
            if r.ok:
                messagebox.showinfo("OK", "Points updated")
            else:
                messagebox.showerror("Error", r.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))
