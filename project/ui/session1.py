import os
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from datetime import datetime, time

from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error
from sklearn.cluster import KMeans

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def show_error(msg: str):
    messagebox.showerror("Ошибка", msg)


def show_info(msg: str):
    messagebox.showinfo("Готово", msg)


class DataManager:
    """
    Хранит пути к исходным CSV. Их можно переуказать через UI.
    """
    def __init__(self):
        self.sales_path: str = ""
        self.products_path: str = ""
        self.customers_path: str = ""

    def load_sales(self) -> pd.DataFrame:
        if not self.sales_path:
            raise FileNotFoundError("Не выбран файл sales_transactions.csv")
        return pd.read_csv(self.sales_path)

    def load_products(self) -> pd.DataFrame:
        if not self.products_path:
            raise FileNotFoundError("Не выбран файл products.csv")
        return pd.read_csv(self.products_path)

    def load_customers(self) -> pd.DataFrame:
        if not self.customers_path:
            raise FileNotFoundError("Не выбран файл customers.csv")
        return pd.read_csv(self.customers_path)


class Session1Frame(ttk.Frame):
    """
    Вкладка Session 1 со всеми заданиями 1.1–1.10.
    Каждое задание запускается отдельной кнопкой.
    """
    def __init__(self, master, data_manager: DataManager, **kwargs):
        super().__init__(master, **kwargs)
        self.dm = data_manager
        self.output_dir = "output_session1"
        ensure_dir(self.output_dir)
        self._build_ui()

    # ---------- UI ----------

    def _build_ui(self):
        top_frame = ttk.Labelframe(self, text="Файлы данных")
        top_frame.pack(fill="x", padx=10, pady=10)

        self.sales_var = tk.StringVar()
        self.products_var = tk.StringVar()
        self.customers_var = tk.StringVar()

        self._file_row(top_frame, "sales_transactions.csv:", self.sales_var,
                       lambda: self._choose_file("sales"))
        self._file_row(top_frame, "products.csv:", self.products_var,
                       lambda: self._choose_file("products"))
        self._file_row(top_frame, "customers.csv:", self.customers_var,
                       lambda: self._choose_file("customers"))

        tasks_frame = ttk.Labelframe(self, text="Задания Session 1")
        tasks_frame.pack(fill="x", padx=10, pady=5)

        btn_opts = dict(width=55)

        buttons = [
            ("1.1 Data Exploration (Session1_DataExploration.txt)", self.task_data_exploration),
            ("1.2 Cleaning (customers_cleaned / sales_transactions_cleaned)", self.task_cleaning),
            ("1.3 Sales Trends (Session1_SalesTrends.pdf)", self.task_sales_trends),
            ("1.4 Product Performance (Session1_ProductPerformance.pdf)", self.task_product_performance),
            ("1.5 Customer Analysis (Session1_CustomerAnalysis.pdf)", self.task_customer_analysis),
            ("1.6 Time Series Forecast (Session1_SalesForecast.csv)", self.task_sales_forecast),
            ("1.7 Segmentation & Recommendations (Session1_Segmentation_and_Recommendations.csv)", self.task_segmentation),
            ("1.8 Product Analysis & Pricing (Session1_Product_Performance.csv / Session1_Price_Analysis.csv)", self.task_price_optimization),
            ("1.9 CLTV (Session1_CLTV.csv)", self.task_cltv),
            ("1.10 Churn Analysis (Session1_Churn_Analysis.csv)", self.task_churn_analysis),
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(tasks_frame, text=text, command=cmd, **btn_opts)
            btn.grid(row=i, column=0, sticky="w", padx=5, pady=2)

        log_frame = ttk.Labelframe(self, text="Лог")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_text = tk.Text(log_frame, height=15)
        self.log_text.pack(fill="both", expand=True)

    def _file_row(self, parent, label, var, cmd):
        row = len(parent.grid_slaves()) // 3
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        entry = ttk.Entry(parent, textvariable=var, width=60, state="readonly")
        entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
        ttk.Button(parent, text="Выбрать", command=cmd).grid(row=row, column=2, padx=5, pady=2)

    def _choose_file(self, kind: str):
        path = filedialog.askopenfilename(
            title="Выберите CSV-файл",
            filetypes=[("CSV", "*.csv"), ("Все файлы", "*.*")]
        )
        if not path:
            return
        if kind == "sales":
            self.dm.sales_path = path
            self.sales_var.set(path)
        elif kind == "products":
            self.dm.products_path = path
            self.products_var.set(path)
        elif kind == "customers":
            self.dm.customers_path = path
            self.customers_var.set(path)

    # ---------- Лог ----------

    def log(self, msg: str):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        print(msg)

    # ---------- 1.1 Data Exploration ----------

    def task_data_exploration(self):
        try:
            sales = self.dm.load_sales()
            products = self.dm.load_products()
            customers = self.dm.load_customers()
        except Exception as e:
            show_error(str(e))
            return

        out_path = os.path.join(self.output_dir, "Session1_DataExploration.txt")
        self.log(f"Создаю {out_path} ...")

        def analyze(df: pd.DataFrame, name: str, related_dfs=None) -> str:
            lines = [f"==== {name} ===="]

            # Типы данных
            lines.append("Типы данных:")
            for col, dtype in df.dtypes.items():
                lines.append(f"  {col}: {dtype}")

            # Недопустимые даты
            invalid_dates_count = 0
            for col in df.columns:
                if "date" in col.lower():
                    parsed = pd.to_datetime(df[col], errors="coerce")
                    invalid_dates_count += parsed.isna().sum()
            lines.append(f"Недопустимые даты: {invalid_dates_count}")

            # Отрицательные значения
            neg_count = 0
            for col in df.select_dtypes(include=[np.number]).columns:
                neg_count += (df[col] < 0).sum()
            lines.append(f"Отрицательные значения в числовых столбцах: {neg_count}")

            # Недопустимые идентификаторы
            if related_dfs:
                for col, (ref_df, ref_col) in related_dfs.items():
                    if col in df.columns and ref_col in ref_df.columns:
                        invalid_ids = ~df[col].isin(ref_df[ref_col])
                        lines.append(f"Недопустимые идентификаторы в {col}: {invalid_ids.sum()}")

            # Неожиданные значения
            cat_cols = df.select_dtypes(include=["object"]).columns
            lines.append("Уникальные значения в категориальных столбцах:")
            for col in cat_cols:
                uniq = df[col].dropna().unique()
                lines.append(f"  {col}: {len(uniq)} уникальных")

            # Проблемы форматирования
            format_issues = 0
            for col in cat_cols:
                s = df[col].astype(str)
                stripped = s.str.strip()
                format_issues += (stripped != s).sum()
            lines.append(f"Проблемы форматирования (лишние пробелы и т.п.): {format_issues}")
            lines.append("")
            return "\n".join(lines)

        parts = []
        parts.append(analyze(
            sales,
            "sales_transactions.csv",
            related_dfs={
                "customer_id": (customers, "customer_id"),
                "product_id": (products, "product_id"),
            }
        ))
        parts.append(analyze(products, "products.csv"))
        parts.append(analyze(customers, "customers.csv"))

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))

        self.log("1.1 Data Exploration завершено.")
        show_info("Session1_DataExploration.txt создан.")

    # ---------- 1.2 Cleaning ----------

    def task_cleaning(self):
        try:
            customers = self.dm.load_customers()
            sales = self.dm.load_sales()
            products = self.dm.load_products()
        except Exception as e:
            show_error(str(e))
            return

        self.log("1.2: очистка данных...")

        # -------------------------------
        # CLEAN CUSTOMERS
        # -------------------------------

        # age → среднее
        if "age" in customers.columns:
            mean_age = customers["age"].dropna().mean()
            customers["age"] = customers["age"].fillna(round(mean_age))

        # phone_number → "0"
        if "phone_number" in customers.columns:
            customers["phone_number"] = customers["phone_number"].fillna("0")

        # нормализация телефона
        if "phone_number" in customers.columns:
            customers["phone_number"] = customers["phone_number"].astype(str).str.replace(
                r"[^\d+]", "", regex=True
            )

        # дата join_date / last_purchase_date → добавляем случайное время
        def add_random_time_to_date(series: pd.Series) -> pd.Series:
            dates = pd.to_datetime(series, errors="coerce")
            out = []
            for d in dates:
                if pd.isna(d):
                    out.append(pd.NaT)
                else:
                    h = random.randint(9, 16)
                    m = random.randint(0, 59)
                    dt = datetime.combine(d.date(), time(h, m))
                    out.append(dt)
            return pd.to_datetime(out)

        for col in customers.columns:
            if "date" in col.lower():
                customers[col] = add_random_time_to_date(customers[col])

        # -------------------------------
        # CLEAN SALES
        # -------------------------------

        # promotion_id → 0
        if "promotion_id" in sales.columns:
            sales["promotion_id"] = sales["promotion_id"].fillna(0)

        # даты → формат + случайное время
        for col in sales.columns:
            if "date" in col.lower():
                sales[col] = add_random_time_to_date(sales[col])

        # -------------------------------
        # CLEAN PRODUCTS (НОВОЕ)
        # -------------------------------

        # переименуем кривые столбцы
        rename_map = {
            "id": "product_id",
            "name": "product_name"
        }
        for old, new in rename_map.items():
            if old in products.columns and new not in products.columns:
                products.rename(columns={old: new}, inplace=True)

        # строки — trim()
        for col in products.select_dtypes(include=["object"]).columns:
            products[col] = products[col].astype(str).str.strip()

        # price / cost → float + NaN = 0
        if "price" in products.columns:
            products["price"] = products["price"].fillna(0).astype(float)
        else:
            products["price"] = 0.0

        if "cost" in products.columns:
            products["cost"] = products["cost"].fillna(0).astype(float)
        else:
            products["cost"] = 0.0

        # seasonal / active → 1 или 0
        for col in ["seasonal", "active"]:
            if col in products.columns:
                products[col] = products[col].astype(str).str.lower()
                products[col] = products[col].replace(
                    {"yes": 1, "true": 1, "1": 1,
                     "no": 0, "false": 0, "0": 0}
                ).astype(int)
            else:
                products[col] = 1

        # ingredients → заполняем пропуски
        if "ingredients" not in products.columns:
            products["ingredients"] = ""
        products["ingredients"] = products["ingredients"].fillna("")

        # introduced_date → корректная дата
        if "introduced_date" in products.columns:
            products["introduced_date"] = pd.to_datetime(
                products["introduced_date"], errors="coerce"
            ).fillna(pd.Timestamp("2000-01-01"))
        else:
            products["introduced_date"] = pd.Timestamp("2000-01-01")

        # -------------------------------
        # SAVE CLEANED FILES
        # -------------------------------

        customers_path = os.path.join(self.output_dir, "customers_cleaned.csv")
        sales_path = os.path.join(self.output_dir, "sales_transactions_cleaned.csv")
        products_path = os.path.join(self.output_dir, "products_cleaned.csv")

        customers.to_csv(customers_path, index=False)
        sales.to_csv(sales_path, index=False)
        products.to_csv(products_path, index=False)

        self.log("1.2 Cleaning завершено.")
        show_info(
            "customers_cleaned.csv, sales_transactions_cleaned.csv и products_cleaned.csv созданы."
        )

    # ---------- 1.3 Sales Trends ----------

    def task_sales_trends(self):
        cleaned_path = os.path.join(self.output_dir, "sales_transactions_cleaned.csv")
        if not os.path.exists(cleaned_path):
            show_error("Сначала выполни задание 1.2 (Cleaning), чтобы создать sales_transactions_cleaned.csv")
            return

        sales = pd.read_csv(cleaned_path)

        date_col = None
        for col in sales.columns:
            if "date" in col.lower():
                date_col = col
                break
        if date_col is None:
            show_error("Не найден столбец даты в sales_transactions_cleaned.csv")
            return

        if "price" not in sales.columns or "quantity" not in sales.columns:
            show_error("В sales_transactions_cleaned.csv должны быть price и quantity")
            return

        sales[date_col] = pd.to_datetime(sales[date_col], errors="coerce")
        sales["revenue"] = sales["price"] * sales["quantity"]
        sales["month"] = sales[date_col].dt.to_period("M").dt.to_timestamp()

        grouped = sales.groupby("month").agg(
            total_revenue=("revenue", "sum"),
            transactions=("transaction_id", "nunique")
        )
        grouped["avg_order_value"] = grouped["total_revenue"] / grouped["transactions"].replace(0, np.nan)

        top3 = grouped.sort_values("total_revenue", ascending=False).head(3)

        plots_dir = os.path.join(self.output_dir, "plots")
        ensure_dir(plots_dir)

        plt.figure()
        grouped["total_revenue"].plot(marker="o")
        plt.title("Общий доход от продаж по месяцам")
        plt.xlabel("Месяц")
        plt.ylabel("Выручка")
        p1 = os.path.join(plots_dir, "sales_total_revenue.png")
        plt.tight_layout()
        plt.savefig(p1)
        plt.close()

        plt.figure()
        grouped["transactions"].plot(marker="o")
        plt.title("Количество транзакций по месяцам")
        plt.xlabel("Месяц")
        plt.ylabel("Кол-во транзакций")
        p2 = os.path.join(plots_dir, "sales_transactions.png")
        plt.tight_layout()
        plt.savefig(p2)
        plt.close()

        plt.figure()
        grouped["avg_order_value"].plot(marker="o")
        plt.title("Средняя стоимость заказа по месяцам")
        plt.xlabel("Месяц")
        plt.ylabel("Средний чек")
        p3 = os.path.join(plots_dir, "sales_aov.png")
        plt.tight_layout()
        plt.savefig(p3)
        plt.close()

        pdf_path = os.path.join(self.output_dir, "Session1_SalesTrends.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "Session1 - Sales Trends")

        y = height - 3 * cm
        for img in [p1, p2, p3]:
            if os.path.exists(img):
                c.drawImage(img, 2 * cm, y - 7 * cm, width=16 * cm, height=6 * cm, preserveAspectRatio=True)
                y -= 7.5 * cm
                if y < 5 * cm:
                    c.showPage()
                    y = height - 2 * cm

        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, height - 2 * cm, "Топ-3 месяцев по выручке")
        c.setFont("Helvetica", 12)
        y = height - 3 * cm
        c.drawString(2 * cm, y, "Месяц")
        c.drawString(8 * cm, y, "Общая выручка")
        y -= 0.7 * cm

        for month, row in top3.iterrows():
            c.drawString(2 * cm, y, str(month.date()))
            c.drawString(8 * cm, y, f"{row['total_revenue']:.2f}")
            y -= 0.6 * cm

        c.save()

        self.log("1.3 Sales Trends завершено.")
        show_info("Session1_SalesTrends.pdf создан.")

    # ---------- 1.4 Product Performance ----------

    def task_product_performance(self):
        cleaned_path = os.path.join(self.output_dir, "sales_transactions_cleaned.csv")
        if not os.path.exists(cleaned_path):
            show_error("Сначала выполни задание 1.2 (Cleaning), чтобы создать sales_transactions_cleaned.csv")
            return

        try:
            sales = pd.read_csv(cleaned_path)
            products = self.dm.load_products()
        except Exception as e:
            show_error(str(e))
            return

        if "product_id" not in sales.columns or "product_id" not in products.columns:
            show_error("В данных должен быть столбец product_id.")
            return
        if "price" not in sales.columns or "quantity" not in sales.columns:
            show_error("В sales_transactions_cleaned.csv должны быть price и quantity.")
            return

        merged = sales.merge(products, on="product_id", how="left")
        merged["revenue"] = merged["price_x"] * merged["quantity"]


        prod_group = merged.groupby(["product_id", "product_name"], as_index=False).agg(
            total_quantity=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
            cost=("cost", "mean"),
        )

        if "category" in merged.columns:
            cat_group = merged.groupby("category")["revenue"].sum()
        else:
            cat_group = pd.Series(dtype=float)

        plots_dir = os.path.join(self.output_dir, "plots")
        ensure_dir(plots_dir)

        cat_img = None
        if not cat_group.empty:
            plt.figure()
            cat_group.plot(kind="bar")
            plt.title("Общий доход по категориям продуктов")
            plt.xlabel("Категория")
            plt.ylabel("Выручка")
            cat_img = os.path.join(plots_dir, "product_category_revenue.png")
            plt.tight_layout()
            plt.savefig(cat_img)
            plt.close()

        top3 = prod_group.sort_values("total_quantity", ascending=False).head(3)

        pdf_path = os.path.join(self.output_dir, "Session1_ProductPerformance.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "Session1 - Product Performance")

        y = height - 3 * cm
        if cat_img and os.path.exists(cat_img):
            c.setFont("Helvetica", 12)
            c.drawString(2 * cm, y, "Гистограмма выручки по категориям:")
            y -= 0.7 * cm
            c.drawImage(cat_img, 2 * cm, y - 8 * cm, width=16 * cm, height=7 * cm, preserveAspectRatio=True)
            c.showPage()

        y = height - 2 * cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, "Топ-3 самых продаваемых продукта")
        y -= 1 * cm
        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, "Название продукта")
        c.drawString(10 * cm, y, "Кол-во")
        c.drawString(14 * cm, y, "Выручка")
        y -= 0.7 * cm

        for _, row in top3.iterrows():
            name = str(row["product_name"])
            c.drawString(2 * cm, y, name[:35])
            c.drawString(10 * cm, y, str(int(row["total_quantity"])))
            c.drawString(14 * cm, y, f"{row['total_revenue']:.2f}")
            y -= 0.7 * cm

        c.save()

        self.log("1.4 Product Performance завершено.")
        show_info("Session1_ProductPerformance.pdf создан.")

    # ---------- 1.5 Customer Analysis ----------

    def task_customer_analysis(self):
        customers_path = os.path.join(self.output_dir, "customers_cleaned.csv")
        if not os.path.exists(customers_path):
            show_error("Сначала выполни задание 1.2 (Cleaning), чтобы создать customers_cleaned.csv")
            return

        customers = pd.read_csv(customers_path)

        plots_dir = os.path.join(self.output_dir, "plots")
        ensure_dir(plots_dir)

        if "age" not in customers.columns:
            show_error("В customers_cleaned.csv нет столбца age.")
            return

        bins = [18, 25, 35, 45, 200]
        labels = ["18-24", "25-34", "35-44", "45+"]

        customers["age_group"] = pd.cut(customers["age"], bins=bins, labels=labels, right=False)

        age_counts = customers["age_group"].value_counts().sort_index()

        plt.figure()
        age_counts.plot(kind="bar")
        plt.title("Распределение заказчиков по возрастным группам")
        plt.xlabel("Возрастная группа")
        plt.ylabel("Число заказчиков")
        age_img = os.path.join(plots_dir, "customer_age_hist.png")
        plt.tight_layout()
        plt.savefig(age_img)
        plt.close()

        if "gender" in customers.columns:
            gender_pct = customers["gender"].value_counts(normalize=True) * 100
        else:
            gender_pct = pd.Series(dtype=float)

        if "membership_status" in customers.columns and "total_spending" in customers.columns:
            loyalty_avg = customers.groupby("membership_status")["total_spending"].mean()
        else:
            loyalty_avg = pd.Series(dtype=float)

        pdf_path = os.path.join(self.output_dir, "Session1_CustomerAnalysis.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "Session1 - Customer Analysis")

        y = height - 3 * cm
        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, "Гистограмма: возрастные группы")
        y -= 0.7 * cm
        if os.path.exists(age_img):
            c.drawImage(age_img, 2 * cm, y - 8 * cm, width=16 * cm, height=7 * cm, preserveAspectRatio=True)
            c.showPage()
        else:
            c.showPage()

        y = height - 2 * cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, "Распределение по полу (%)")
        y -= 1 * cm
        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, "Пол")
        c.drawString(6 * cm, y, "Процент")
        y -= 0.7 * cm

        for g, pct in gender_pct.items():
            c.drawString(2 * cm, y, str(g))
            c.drawString(6 * cm, y, f"{pct:.2f}%")
            y -= 0.6 * cm

        y -= 1 * cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, "Средние расходы по статусу членства")
        y -= 1 * cm
        c.setFont("Helvetica", 12)
        c.drawString(2 * cm, y, "Статус")
        c.drawString(8 * cm, y, "Средние расходы")
        y -= 0.7 * cm

        for lvl, avg_val in loyalty_avg.items():
            c.drawString(2 * cm, y, str(lvl))
            c.drawString(8 * cm, y, f"{avg_val:.2f}")
            y -= 0.6 * cm

        c.save()

        self.log("1.5 Customer Analysis завершено.")
        show_info("Session1_CustomerAnalysis.pdf создан.")

    # ---------- 1.6 Time Series Forecast (ARIMA) ----------

    def task_sales_forecast(self):
        cleaned_path = os.path.join(self.output_dir, "sales_transactions_cleaned.csv")
        if not os.path.exists(cleaned_path):
            show_error("Сначала выполни задание 1.2 (Cleaning), чтобы создать sales_transactions_cleaned.csv")
            return

        sales = pd.read_csv(cleaned_path)

        date_col = None
        for col in sales.columns:
            if "date" in col.lower():
                date_col = col
                break
        if date_col is None:
            show_error("Не найден столбец даты в sales_transactions_cleaned.csv")
            return

        if "price" not in sales.columns or "quantity" not in sales.columns:
            show_error("В sales_transactions_cleaned.csv должны быть price и quantity.")
            return

        sales[date_col] = pd.to_datetime(sales[date_col], errors="coerce")
        sales["revenue"] = sales["price"] * sales["quantity"]

        daily = sales.groupby(sales[date_col].dt.date)["revenue"].sum().sort_index()
        daily.index = pd.to_datetime(daily.index)
        series = daily.asfreq("D").fillna(0)

        if len(series) < 10:
            show_error("Слишком мало точек для ARIMA-прогноза.")
            return

        model = ARIMA(series, order=(1, 1, 1))
        model_fit = model.fit()
        forecast_steps = 30
        forecast = model_fit.forecast(steps=forecast_steps)

        pred_in_sample = model_fit.predict(start=0, end=len(series) - 1)
        mae = mean_absolute_error(series, pred_in_sample)
        self.log(f"1.6: MAE ARIMA = {mae:.2f}")

        forecast_index = pd.date_range(series.index[-1] + pd.Timedelta(days=1),
                                       periods=forecast_steps, freq="D")
        out_df = pd.DataFrame({
            "Date": forecast_index.strftime("%Y-%m-%d"),
            "Predicted_Sales": forecast.values
        })

        out_path = os.path.join(self.output_dir, "Session1_SalesForecast.csv")
        out_df.to_csv(out_path, index=False)

        self.log("1.6 Sales Forecast завершено.")
        show_info("Session1_SalesForecast.csv создан.")

    # ---------- 1.7 Segmentation & Recommendations ----------

    def task_segmentation(self):
        cust_path = os.path.join(self.output_dir, "customers_cleaned.csv")
        sales_path = os.path.join(self.output_dir, "sales_transactions_cleaned.csv")
        if not (os.path.exists(cust_path) and os.path.exists(sales_path)):
            show_error("Нужны customers_cleaned.csv и sales_transactions_cleaned.csv.\nСначала сделай 1.2 (Cleaning).")
            return

        customers = pd.read_csv(cust_path)
        sales = pd.read_csv(sales_path)

        if "customer_id" not in customers.columns or "customer_id" not in sales.columns:
            show_error("Не найден customer_id.")
            return
        if "product_id" not in sales.columns:
            show_error("Не найден product_id.")
            return
        if "price" not in sales.columns or "quantity" not in sales.columns:
            show_error("В sales_transactions_cleaned.csv должны быть price и quantity.")
            return

        self.log("1.7: сегментация заказчиков и рекомендации...")

        sales["revenue"] = sales["price"] * sales["quantity"]

        if "transaction_id" in sales.columns:
            trans_group = sales.groupby(["customer_id", "transaction_id"]).agg(
                transaction_revenue=("revenue", "sum")
            ).reset_index()
        else:
            trans_group = sales.copy()
            trans_group["transaction_revenue"] = trans_group["revenue"]

        total_purchases = trans_group.groupby("customer_id")["transaction_revenue"].count()
        total_revenue = trans_group.groupby("customer_id")["transaction_revenue"].sum()

        cust_metrics = pd.DataFrame({
            "customer_id": total_purchases.index,
            "total_purchases": total_purchases.values,
            "total_revenue": total_revenue.values
        })
        cust_metrics["avg_purchase_value"] = cust_metrics["total_revenue"] / cust_metrics["total_purchases"].replace(0, 1)

        merged_cust = customers.merge(
            cust_metrics[["customer_id", "total_purchases", "avg_purchase_value"]],
            on="customer_id", how="left"
        )
        merged_cust["total_purchases"] = merged_cust["total_purchases"].fillna(0)
        merged_cust["avg_purchase_value"] = merged_cust["avg_purchase_value"].fillna(0)

        X = merged_cust[["total_purchases", "avg_purchase_value"]].to_numpy()

        if np.all(X == 0):
            show_error("Все total_purchases и avg_purchase_value равны 0 — кластеризация невозможна.")
            return

        try:
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
        except Exception as e:
            show_error(f"Ошибка K-means: {e}")
            return

        merged_cust["cluster_label"] = labels + 1
        cluster_by_customer = merged_cust.set_index("customer_id")["cluster_label"]

        # co-occurrence продуктов
        co_counts = {}
        if "transaction_id" in sales.columns:
            by_trans = sales.groupby("transaction_id")["product_id"].apply(set)
            for prods in by_trans:
                prods = list(prods)
                for i in range(len(prods)):
                    p = prods[i]
                    co_counts.setdefault(p, {})
                    for j in range(len(prods)):
                        if i == j:
                            continue
                        q = prods[j]
                        co_counts[p][q] = co_counts[p].get(q, 0) + 1

        purchased_by_customer = sales.groupby("customer_id")["product_id"].apply(set)

        # частоты продуктов по кластерам
        cluster_product_freq = {}
        for _, row in sales.iterrows():
            cid = row["customer_id"]
            pid = row["product_id"]
            if cid not in cluster_by_customer:
                continue
            cluster = int(cluster_by_customer.loc[cid])
            cluster_product_freq.setdefault(cluster, {})
            cluster_product_freq[cluster][pid] = cluster_product_freq[cluster].get(pid, 0) + 1

        rows_out = []
        for _, row in merged_cust.iterrows():
            cid = row["customer_id"]
            cluster = int(row["cluster_label"])
            already = purchased_by_customer.get(cid, set())

            cluster_freq = cluster_product_freq.get(cluster, {})
            candidates = sorted(cluster_freq.items(), key=lambda x: x[1], reverse=True)
            cand_ids = [pid for pid, _ in candidates]

            recs = []
            for pid in cand_ids:
                if pid not in already and pid not in recs:
                    recs.append(pid)
                if len(recs) >= 3:
                    break
            while len(recs) < 3:
                recs.append(np.nan)

            rows_out.append({
                "customer_id": cid,
                "cluster_label": cluster,
                "recommended_product_1": recs[0],
                "recommended_product_2": recs[1],
                "recommended_product_3": recs[2],
            })

        out_df = pd.DataFrame(rows_out)
        out_path = os.path.join(self.output_dir, "Session1_Segmentation_and_Recommendations.csv")
        out_df.to_csv(out_path, index=False)

        self.log("1.7 Segmentation & Recommendations завершено.")
        show_info("Session1_Segmentation_and_Recommendations.csv создан.")

    # ---------- 1.8 Product Analysis & Price Optimization ----------

    def task_price_optimization(self):
        sales_path = os.path.join(self.output_dir, "sales_transactions_cleaned.csv")
        if not os.path.exists(sales_path):
            show_error("Сначала выполни 1.2 (Cleaning), чтобы создать sales_transactions_cleaned.csv.")
            return
        try:
            sales = pd.read_csv(sales_path)
            products = self.dm.load_products()
        except Exception as e:
            show_error(str(e))
            return

        if "product_id" not in sales.columns or "product_id" not in products.columns:
            show_error("В данных должен быть product_id.")
            return
        if "price" not in sales.columns or "quantity" not in sales.columns:
            show_error("В sales_transactions_cleaned.csv должны быть price и quantity.")
            return
        if "cost" not in products.columns:
            show_error("В products.csv нет столбца cost.")
            return

        self.log("1.8: анализ характеристик продукта и цен...")

        date_col = None
        for col in sales.columns:
            if "date" in col.lower():
                date_col = col
                break
        if date_col is None:
            show_error("Не найден столбец даты в sales_transactions_cleaned.csv.")
            return

        sales[date_col] = pd.to_datetime(sales[date_col], errors="coerce")
        sales["revenue"] = sales["price"] * sales["quantity"]

        perf = sales.groupby("product_id").agg(
            total_quantity_sold=("quantity", "sum"),
            total_revenue=("revenue", "sum")
        ).reset_index()

        prod_cost = products[["product_id", "cost"]].copy()
        perf = perf.merge(prod_cost, on="product_id", how="left")
        perf["cost"] = perf["cost"].fillna(0)

        perf["total_cost"] = perf["total_quantity_sold"] * perf["cost"]
        perf["profit_margin"] = np.where(
            perf["total_revenue"] > 0,
            (perf["total_revenue"] - perf["total_cost"]) / perf["total_revenue"],
            0.0
        )

        perf_out = perf[["product_id", "total_quantity_sold", "total_revenue", "profit_margin"]]
        perf_path = os.path.join(self.output_dir, "Session1_Product_Performance.csv")
        perf_out.to_csv(perf_path, index=False)

        # ценовая эластичность
        sales["month"] = sales[date_col].dt.to_period("M").dt.to_timestamp()

        monthly = sales.groupby(["product_id", "month"]).agg(
            q=("quantity", "sum"),
            p=("price", "mean")
        ).reset_index()

        ped_rows = []
        for pid, grp in monthly.groupby("product_id"):
            grp = grp.sort_values("month")
            if len(grp) < 2 or grp["p"].nunique() == 1:
                ped = 0.0
                sug = 0.0
            else:
                q1 = grp.iloc[0]["q"]
                p1 = grp.iloc[0]["p"]
                q2 = grp.iloc[-1]["q"]
                p2 = grp.iloc[-1]["p"]

                q_avg = (q1 + q2) / 2 if (q1 + q2) != 0 else 1
                p_avg = (p1 + p2) / 2 if (p1 + p2) != 0 else 1

                dq = q2 - q1
                dp = p2 - p1

                if dp == 0 or p_avg == 0 or q_avg == 0:
                    ped = 0.0
                else:
                    ped = (dq / q_avg) / (dp / p_avg)

                abs_ped = abs(ped)
                if abs_ped > 1.2:
                    sug = -5.0
                elif abs_ped < 0.5:
                    sug = 5.0
                else:
                    sug = 0.0

            ped_rows.append({
                "product_id": pid,
                "price_elasticity_of_demand": ped,
                "suggested_price_change": sug
            })

        ped_df = pd.DataFrame(ped_rows)
        ped_path = os.path.join(self.output_dir, "Session1_Price_Analysis.csv")
        ped_df.to_csv(ped_path, index=False)

        self.log("1.8 Product Performance & Price Analysis завершено.")
        show_info("Session1_Product_Performance.csv и Session1_Price_Analysis.csv созданы.")

    # ---------- 1.9 CLTV ----------

    def task_cltv(self):
        sales_path = os.path.join(self.output_dir, "sales_transactions_cleaned.csv")
        if not os.path.exists(sales_path):
            show_error("Сначала выполни 1.2 (Cleaning), чтобы создать sales_transactions_cleaned.csv.")
            return

        sales = pd.read_csv(sales_path)

        if "customer_id" not in sales.columns:
            show_error("В sales_transactions_cleaned.csv нет customer_id.")
            return

        date_col = None
        for col in sales.columns:
            if "date" in col.lower():
                date_col = col
                break
        if date_col is None:
            show_error("Не найден столбец даты в sales_transactions_cleaned.csv.")
            return

        if "price" not in sales.columns or "quantity" not in sales.columns:
            show_error("В sales_transactions_cleaned.csv должны быть price и quantity.")
            return

        sales[date_col] = pd.to_datetime(sales[date_col], errors="coerce")
        sales["revenue"] = sales["price"] * sales["quantity"]

        if "transaction_id" in sales.columns:
            trans_group = sales.groupby(["customer_id", "transaction_id"]).agg(
                transaction_revenue=("revenue", "sum"),
                date=(date_col, "min")
            ).reset_index()
        else:
            trans_group = sales.copy()
            trans_group["transaction_revenue"] = trans_group["revenue"]
            trans_group["date"] = trans_group[date_col]

        avg_purchase = trans_group.groupby("customer_id")["transaction_revenue"].mean()

        cust_dates = trans_group.groupby("customer_id")["date"].agg(["min", "max", "count"])
        month_diff = (cust_dates["max"] - cust_dates["min"]).dt.days / 30.0
        month_diff = month_diff.replace(0, 1)
        frequency = cust_dates["count"] / month_diff

        cltv = (avg_purchase * frequency * 36).round(2)

        out_df = pd.DataFrame({
            "customer_id": cltv.index.astype(int),
            "cltv": cltv.values
        })

        out_path = os.path.join(self.output_dir, "Session1_CLTV.csv")
        out_df.to_csv(out_path, index=False)

        self.log("1.9 CLTV рассчитан.")
        show_info("Session1_CLTV.csv создан.")

    # ---------- 1.10 Churn Analysis ----------

    def task_churn_analysis(self):
        cust_path = os.path.join(self.output_dir, "customers_cleaned.csv")
        cltv_path = os.path.join(self.output_dir, "Session1_CLTV.csv")
        if not (os.path.exists(cust_path) and os.path.exists(cltv_path)):
            show_error("Нужны customers_cleaned.csv и Session1_CLTV.csv.\nСначала сделай 1.2 и 1.9.")
            return

        customers = pd.read_csv(cust_path)
        cltv = pd.read_csv(cltv_path)

        if "customer_id" not in customers.columns:
            show_error("В customers_cleaned.csv нет customer_id.")
            return
        if "churn" not in customers.columns:
            show_error("В customers_cleaned.csv нет столбца churn.")
            return

        merged = customers.merge(cltv, on="customer_id", how="left")

        churned_mask = merged["churn"].astype(str).str.lower().isin(["yes", "1", "true"])
        churn_rate = churned_mask.mean() * 100.0

        avg_cltv_churned = merged.loc[churned_mask, "cltv"].mean()
        avg_cltv_active = merged.loc[~churned_mask, "cltv"].mean()

        out_df = pd.DataFrame({
            "churn_rate": [round(churn_rate, 2)],
            "avg_cltv_churned": [round(avg_cltv_churned, 2) if not np.isnan(avg_cltv_churned) else np.nan],
            "avg_cltv_active": [round(avg_cltv_active, 2) if not np.isnan(avg_cltv_active) else np.nan]
        })

        out_path = os.path.join(self.output_dir, "Session1_Churn_Analysis.csv")
        out_df.to_csv(out_path, index=False)

        self.log("1.10 Churn Analysis завершено.")
        show_info("Session1_Churn_Analysis.csv создан.")
