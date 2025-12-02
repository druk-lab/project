import os
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


class Session2Frame(ttk.Frame):
    """
    Session 2 — System Design (Use Cases, ERD, Wireframes, API Design).
    Сделано полностью в стиле Session1.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.output_dir = "output_session2"
        os.makedirs(self.output_dir, exist_ok=True)

        self._build_ui()

    # =====================================================================
    #                               UI
    # =====================================================================

    def _build_ui(self):
        # Панель заголовка + описание модуля
        header = ttk.LabelFrame(self, text="System Design — Session 2", padding=10)
        header.pack(fill="x", padx=10, pady=10)

        ttk.Label(header, text="В этой сессии выполняется проектирование системы:").pack(anchor="w")
        ttk.Label(header, text="• Use Cases\n• ERD\n• Wireframes\n• Customer API Design").pack(anchor="w")

        # Панель кнопок
        task_frame = ttk.LabelFrame(self, text="Задания Session 2", padding=10)
        task_frame.pack(fill="x", padx=10, pady=10)

        btn_opts = dict(width=50)

        ttk.Button(task_frame, text="2.1 — Generate Use Case Diagram (PDF)",
                   command=self.generate_usecase).pack(pady=3)
        ttk.Button(task_frame, text="2.2 — Generate ERD (PDF)",
                   command=self.generate_erd).pack(pady=3)
        ttk.Button(task_frame, text="2.3 — Generate Wireframes (PDF)",
                   command=self.generate_wireframes).pack(pady=3)
        ttk.Button(task_frame, text="2.4 — Generate Customer API Design (TXT)",
                   command=self.generate_api).pack(pady=3)
        ttk.Button(task_frame, text="2.5 — Generate ALL",
                   command=self.generate_all).pack(pady=10)

        # ЛОГ
        log_frame = ttk.LabelFrame(self, text="Лог", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_text = tk.Text(log_frame, height=15)
        self.log_text.pack(fill="both", expand=True)

    # =====================================================================
    #                               LOG
    # =====================================================================

    def log(self, msg: str):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        print(msg)

    # =====================================================================
    #                   2.1 — USE CASES (PDF)
    # =====================================================================

    def generate_usecase(self):
        out = os.path.join(self.output_dir, "Session2_UseCases.pdf")
        c = canvas.Canvas(out, pagesize=A4)
        w, h = A4

        def draw_stickman(x, y):
            """Рисует человечка (актора)"""
            # head
            c.circle(x, y, 10)
            # body
            c.line(x, y - 10, x, y - 40)
            # arms
            c.line(x - 15, y - 20, x + 15, y - 20)
            # legs
            c.line(x, y - 40, x - 15, y - 60)
            c.line(x, y - 40, x + 15, y - 60)

        def draw_usecase(x, y, text):
            """Рисует овал и текст use case"""
            c.ellipse(x - 70, y - 25, x + 70, y + 25)
            c.setFont("Helvetica", 10)
            text_width = c.stringWidth(text, "Helvetica", 10)
            c.drawString(x - text_width/2, y - 5, text)

        # Заголовок
        c.setFont("Helvetica-Bold", 18)
        c.drawString(2 * cm, h - 2 * cm, "Use Case Diagram — Belle Croissant Lyonnais")

        # --- Акторы ---
        # Customer
        draw_stickman(3 * cm, h - 6 * cm)
        c.setFont("Helvetica", 12)
        c.drawString(2.3 * cm, h - 7.5 * cm, "Customer")

        # Employee
        draw_stickman(3 * cm, h - 14 * cm)
        c.drawString(2.3 * cm, h - 15.5 * cm, "Employee")

        # --- Use Cases ---
        usecases_customer = [
            "Browse Products",
            "Place Order",
            "Track Order Status"
        ]

        usecases_employee = [
            "Manage Inventory",
            "Apply Promotion",
            "Manage Customers"
        ]

        # Расположение use cases
        uc_y = h - 5.5 * cm
        for uc in usecases_customer:
            draw_usecase(11 * cm, uc_y, uc)
            c.line(3 * cm, uc_y, 9.3 * cm, uc_y)  # связь с актором
            uc_y -= 3 * cm

        uc_y = h - 13 * cm
        for uc in usecases_employee:
            draw_usecase(11 * cm, uc_y, uc)
            c.line(3 * cm, uc_y, 9.3 * cm, uc_y)
            uc_y -= 3 * cm

        c.save()
        self.log("Use Case Diagram создан.")
        messagebox.showinfo("Готово", "Use Case Diagram создан!")


    # =====================================================================
    #                        2.2 — ERD (PDF)
    # =====================================================================

    def generate_erd(self):
        out = os.path.join(self.output_dir, "Session2_ERD.pdf")
        c = canvas.Canvas(out, pagesize=A4)
        w, h = A4

        c.setFont("Helvetica-Bold", 18)
        c.drawString(2 * cm, h - 2 * cm, "Entity Relationship Diagram (ERD)")

        c.setFont("Helvetica", 12)

        # --- Таблицы ---
        boxes = [
            ("Customers", ["customer_id (PK)", "name", "phone", "email"]),
            ("Products", ["product_id (PK)", "name", "price", "category"]),
            ("Orders", ["order_id (PK)", "customer_id (FK)", "date", "total"]),
            ("OrderItems", ["item_id (PK)", "order_id (FK)", "product_id (FK)", "quantity"]),
            ("Promotions", ["promotion_id (PK)", "type", "discount"]),
            ("Loyalty", ["loyalty_id (PK)", "customer_id (FK)", "level"])
        ]

        x = 2 * cm
        y = h - 4 * cm

        for name, fields in boxes:
            c.rect(x, y - 3 * cm, 7 * cm, 2.5 * cm)
            c.drawString(x + 5, y - 0.4 * cm, name)

            fy = y - 1 * cm
            for f in fields:
                c.drawString(x + 10, fy, f"- {f}")
                fy -= 0.45 * cm

            x += 8 * cm
            if x > w - 10 * cm:
                x = 2 * cm
                y -= 4 * cm

        c.save()
        self.log("ERD создан.")

    # =====================================================================
    #                       2.3 — WIREFRAMES (PDF)
    # =====================================================================

    def generate_wireframes(self):
        out = os.path.join(self.output_dir, "Session2_Wireframes.pdf")
        c = canvas.Canvas(out, pagesize=A4)
        w, h = A4

        c.setFont("Helvetica-Bold", 18)
        c.drawString(2 * cm, h - 2 * cm, "Wireframes")

        frames = [
            "Login Screen",
            "Dashboard",
            "Product List",
            "Order Details"
        ]

        y = h - 4 * cm

        for title in frames:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2 * cm, y, title)

            c.setFont("Helvetica", 12)
            c.rect(2 * cm, y - 9 * cm, w - 4 * cm, 8 * cm)

            y -= 10 * cm
            if y < 5 * cm:
                c.showPage()
                y = h - 4 * cm

        c.save()
        self.log("Wireframes PDF создан.")

    # =====================================================================
    #                      2.4 — API DESIGN (TXT)
    # =====================================================================

    def generate_api(self):
        out = os.path.join(self.output_dir, "Session2_API_Design.txt")

        endpoints = [
            "GET /api/customers",
            "POST /api/customers",
            "GET /api/products",
            "POST /api/orders",
            "GET /api/orders/<id>",
        ]

        with open(out, "w", encoding="utf-8") as f:
            f.write("Belle Croissant Lyonnais — Customer API Design\n\n")
            f.write("Endpoints:\n")
            for ep in endpoints:
                f.write(f"- {ep}\n")

            f.write("\nExample JSON:\n")
            f.write("{\n")
            f.write('  "customer_id": 1,\n')
            f.write('  "name": "John Doe",\n')
            f.write('  "orders": [101, 102]\n')
            f.write("}\n")

        self.log("API Design создан.")

    # =====================================================================
    #                     2.5 — Generate ALL
    # =====================================================================

    def generate_all(self):
        self.generate_usecase()
        self.generate_erd()
        self.generate_wireframes()
        self.generate_api()
        self.log("Session 2 — все файлы созданы.")
