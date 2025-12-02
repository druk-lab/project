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


class Session3OrdersFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.build_ui()

    # =====================================================
    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Обновить", command=self.load_orders).pack(side="left")
        ttk.Button(top, text="Создать заказ", command=self.new_order_window).pack(side="left", padx=5)

        # Поиск
        self.search_var = tk.StringVar()
        ttk.Label(top, text="Поиск:").pack(side="left", padx=10)
        ttk.Entry(top, textvariable=self.search_var, width=40).pack(side="left")
        ttk.Button(top, text="Найти", command=self.search_orders).pack(side="left", padx=5)

        # Таблица
        self.table = ttk.Treeview(
            self,
            columns=("id", "customer", "date", "total", "status"),
            show="headings",
            height=20
        )
        self.table.pack(fill="both", expand=True, padx=10, pady=10)
        for col, label, w in [
            ("id", "ID", 60),
            ("customer", "Покупатель", 180),
            ("date", "Дата", 160),
            ("total", "Сумма", 80),
            ("status", "Статус", 100),
        ]:
            self.table.heading(col, text=label)
            self.table.column(col, width=w)

        self.table.bind("<Double-1>", self.on_open)

        self.load_orders()

    # =====================================================
    def load_orders(self):
        try:
            r = requests.get(f"{API_URL}/orders", auth=AUTH)
            if r.status_code != 200:
                show_error(r.text)
                return

            data = r.json()
            self.table.delete(*self.table.get_children())
            for o in data:
                self.table.insert("", "end", values=(
                    o["id"],
                    o["customer_name"],
                    o["order_date"],
                    o["total_amount"],
                    o["status"],
                ))
        except Exception as e:
            show_error(str(e))

    def search_orders(self):
        text = self.search_var.get().lower()
        for row in self.table.get_children():
            vals = self.table.item(row)["values"]
            visible = any(text in str(v).lower() for v in vals)
            if visible:
                self.table.reattach(row, "", "end")
            else:
                self.table.detach(row)

    # =====================================================
    #        ОТКРЫТИЕ ЗАКАЗА (двойной клик)
    # =====================================================
    def on_open(self, event):
        selected = self.table.focus()
        if not selected:
            return
        oid = self.table.item(selected)["values"][0]
        self.open_order_window(oid)

    # =====================================================
    #          ОКНО ПРОСМОТРА / УПРАВЛЕНИЯ ЗАКАЗОМ
    # =====================================================
    def open_order_window(self, order_id):
        win = tk.Toplevel(self)
        win.title(f"Заказ #{order_id}")
        win.geometry("500x600")

        try:
            r = requests.get(f"{API_URL}/orders/{order_id}", auth=AUTH)
            if r.status_code != 200:
                show_error(r.text)
                return
            data = r.json()
        except Exception as e:
            show_error(str(e))
            return

        ttk.Label(win, text=f"Покупатель: {data['customer_name']}").pack(anchor="w", padx=10, pady=5)
        ttk.Label(win, text=f"Дата: {data['order_date']}").pack(anchor="w", padx=10)

        ttk.Label(win, text=f"Статус: {data['status']}").pack(anchor="w", padx=10, pady=10)

        frame_items = ttk.LabelFrame(win, text="Позиции")
        frame_items.pack(fill="both", expand=True, padx=10, pady=10)

        table = ttk.Treeview(
            frame_items,
            columns=("id", "name", "qty", "price"),
            show="headings",
            height=10
        )
        table.pack(fill="both", expand=True)

        for col, label, w in [
            ("id", "ID", 50),
            ("name", "Продукт", 200),
            ("qty", "Кол-во", 80),
            ("price", "Цена", 80),
        ]:
            table.heading(col, text=label)
            table.column(col, width=w)

        for it in data["items"]:
            table.insert("", "end", values=(
                it["id"],
                it["product_name"],
                it["quantity"],
                it["unit_price"],
            ))

        # Кнопки управления заказом
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Processing",
                   command=lambda: self.update_order(order_id, "processing", win)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Complete",
                   command=lambda: self.update_order(order_id, "complete", win)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel",
                   command=lambda: self.update_order(order_id, "cancel", win)).pack(side="left", padx=5)

    # =====================================================
    def update_order(self, oid, action, win):
        try:
            r = requests.put(f"{API_URL}/orders/{oid}/{action}", auth=AUTH)
            if r.status_code != 200:
                show_error(r.text)
                return

            show_info("Статус обновлён")
            win.destroy()
            self.load_orders()
        except Exception as e:
            show_error(str(e))

    # =====================================================
    #                СОЗДАНИЕ НОВОГО ЗАКАЗА
    # =====================================================
    def new_order_window(self):
        win = tk.Toplevel(self)
        win.title("Новый заказ")
        win.geometry("450x500")

        ttk.Label(win, text="ID покупателя:").pack(anchor="w", padx=10, pady=5)
        cid_var = tk.StringVar()
        ttk.Entry(win, textvariable=cid_var).pack(fill="x", padx=10)

        items_frame = ttk.LabelFrame(win, text="Товары")
        items_frame.pack(fill="both", expand=True, padx=10, pady=10)

        items = []

        def add_item():
            pid = pid_var.get()
            qty = qty_var.get()
            if not pid or not qty:
                show_error("Укажите product_id и количество")
                return
            try:
                qty = int(qty)
            except:
                show_error("Количество должно быть числом")
                return

            items.append({"product_id": int(pid), "quantity": qty})
            listbox.insert("end", f"PID={pid}, Qty={qty}")

        pid_var = tk.StringVar()
        qty_var = tk.StringVar()

        ttk.Label(items_frame, text="Product ID:").pack(anchor="w")
        ttk.Entry(items_frame, textvariable=pid_var).pack(fill="x")

        ttk.Label(items_frame, text="Quantity:").pack(anchor="w")
        ttk.Entry(items_frame, textvariable=qty_var).pack(fill="x")

        ttk.Button(items_frame, text="Добавить", command=add_item).pack(pady=5)

        listbox = tk.Listbox(items_frame, height=10)
        listbox.pack(fill="both", expand=True)

        # Сохранение
        def save_order():
            if not items:
                show_error("Нет товаров в заказе")
                return

            payload = {
                "customer_id": int(cid_var.get()),
                "items": items
            }

            try:
                r = requests.post(f"{API_URL}/orders", json=payload, auth=AUTH)
                if r.status_code != 201:
                    show_error(r.text)
                else:
                    show_info("Заказ создан")
                    win.destroy()
                    self.load_orders()
            except Exception as e:
                show_error(str(e))

        ttk.Button(win, text="Создать заказ", command=save_order).pack(pady=10)
