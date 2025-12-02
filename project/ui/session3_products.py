import tkinter as tk
from tkinter import ttk, messagebox
import requests
from requests.auth import HTTPBasicAuth

API_URL = "http://127.0.0.1:5000/api"
AUTH = HTTPBasicAuth("staff", "BCLyon2024")


def show_error(msg):
    messagebox.showerror("Ошибка", msg)


def show_info(msg):
    messagebox.showinfo("Готово", msg)


class Session3ProductsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.build_ui()

    # =====================================================
    #                       UI
    # =====================================================
    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Обновить список", command=self.load_products).pack(side="left")
        ttk.Button(top, text="Добавить продукт", command=self.add_product_window).pack(side="left", padx=5)

        # Поиск
        self.search_var = tk.StringVar()
        ttk.Label(top, text="Поиск:").pack(side="left", padx=10)
        ttk.Entry(top, textvariable=self.search_var, width=40).pack(side="left")
        ttk.Button(top, text="Найти", command=self.search_products).pack(side="left", padx=5)

        # ================== TABLE ==================
        self.table = ttk.Treeview(
            self,
            columns=("id", "name", "category", "price", "stock"),
            show="headings",
            height=20
        )
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        for col, label, w in [
            ("id", "ID", 50),
            ("name", "Название", 200),
            ("category", "Категория", 150),
            ("price", "Цена", 80),
            ("stock", "Stock", 60),
        ]:
            self.table.heading(col, text=label)
            self.table.column(col, width=w)

        # Двойной клик — открыть продукт
        self.table.bind("<Double-1>", self.on_edit)

        self.load_products()

    # =====================================================
    #                     ЗАГРУЗКА ДАННЫХ
    # =====================================================
    def load_products(self):
        try:
            r = requests.get(f"{API_URL}/products", auth=AUTH)
            if r.status_code != 200:
                show_error(f"Ошибка загрузки: {r.text}")
                return

            data = r.json()
            self.table.delete(*self.table.get_children())
            for p in data:
                self.table.insert("", "end", values=(
                    p["id"],
                    p["name"],
                    p["category"],
                    p["price"],
                    p["stock"],
                ))
        except Exception as e:
            show_error(str(e))

    def search_products(self):
        text = self.search_var.get().lower()
        for row in self.table.get_children():
            vals = self.table.item(row)["values"]
            visible = any(text in str(v).lower() for v in vals)
            if visible:
                self.table.reattach(row, "", "end")
            else:
                self.table.detach(row)

    # =====================================================
    #                     ОКНО ДОБАВЛЕНИЯ
    # =====================================================
    def add_product_window(self):
        self.open_product_form()

    def on_edit(self, event):
        selected = self.table.focus()
        if not selected:
            return
        pid = self.table.item(selected)["values"][0]
        self.open_product_form(pid)

    # =====================================================
    #                     ФОРМА ПРОДУКТА
    # =====================================================
    def open_product_form(self, product_id=None):
        win = tk.Toplevel(self)
        win.title("Продукт")
        win.geometry("350x500")

        fields = {
            "name": "Название",
            "category": "Категория",
            "price": "Цена",
            "cost": "Себестоимость",
            "description": "Описание",
            "seasonal": "Seasonal (0/1)",
            "active": "Active (0/1)",
            "introduced_date": "Дата",
            "stock": "Stock"
        }

        entries = {}

        row = 0
        for key, label in fields.items():
            ttk.Label(win, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ent = ttk.Entry(win, width=30)
            ent.grid(row=row, column=1, pady=4)
            entries[key] = ent
            row += 1

        # Если редактируем — загрузить данные
        if product_id:
            try:
                r = requests.get(f"{API_URL}/products/{product_id}", auth=AUTH)
                if r.status_code == 200:
                    data = r.json()
                    for k in entries:
                        entries[k].insert(0, data.get(k, ""))
                else:
                    show_error("Не удалось загрузить продукт")
            except Exception as e:
                show_error(str(e))

        # КНОПКИ
        def save():
            payload = {k: entries[k].get() for k in entries}
            for key in ["price", "cost", "stock"]:
                try:
                    payload[key] = float(payload[key])
                except:
                    payload[key] = 0

            payload["seasonal"] = payload["seasonal"] in ("1", "true", "True")
            payload["active"] = payload["active"] in ("1", "true", "True")

            try:
                if product_id:
                    r = requests.put(f"{API_URL}/products/{product_id}", json=payload, auth=AUTH)
                else:
                    r = requests.post(f"{API_URL}/products", json=payload, auth=AUTH)

                if r.status_code not in (200, 201):
                    show_error(r.text)
                else:
                    show_info("Сохранено!")
                    win.destroy()
                    self.load_products()
            except Exception as e:
                show_error(str(e))

        ttk.Button(win, text="Сохранить", command=save).grid(row=row, column=0, pady=10)
        ttk.Button(win, text="Удалить",
                   command=lambda: self.delete_product(product_id, win) if product_id else None,
                   state=("normal" if product_id else "disabled")).grid(row=row, column=1, pady=10)

    def delete_product(self, pid, win):
        if not messagebox.askyesno("Удаление", "Удалить продукт?"):
            return

        try:
            r = requests.delete(f"{API_URL}/products/{pid}", auth=AUTH)
            if r.status_code == 200:
                show_info("Удалено.")
                win.destroy()
                self.load_products()
            else:
                show_error(r.text)
        except Exception as e:
            show_error(str(e))
