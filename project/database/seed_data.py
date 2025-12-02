import pandas as pd
import os
from .connection import get_connection

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_session1")

def seed_from_csv():
    conn = get_connection()
    cur = conn.cursor()

    products_csv  = os.path.join(OUTPUT_DIR, "products_cleaned.csv")
    customers_csv = os.path.join(OUTPUT_DIR, "customers_cleaned.csv")
    sales_csv     = os.path.join(OUTPUT_DIR, "sales_transactions_cleaned.csv")

    # ---------- PRODUCTS ----------
    if os.path.exists(products_csv):
        df = pd.read_csv(products_csv)
        for _, row in df.iterrows():
            cur.execute("""
                INSERT OR REPLACE INTO products
                (id, name, category, price, cost, description, seasonal, active, introduced_date, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["product_id"]),
                row.get("product_name", ""),
                row.get("category", ""),
                float(row.get("price", 0)),
                float(row.get("cost", 0)),
                row.get("ingredients", ""),
                int(row.get("seasonal", 0)),
                int(row.get("active", 1)),
                str(row.get("introduced_date", "")),
                int(row.get("stock", 50)),
            ))

    # ---------- CUSTOMERS ----------
    if os.path.exists(customers_csv):
        df = pd.read_csv(customers_csv)
        for _, row in df.iterrows():
            cur.execute("""
                INSERT OR REPLACE INTO customers
                (id, first_name, last_name, email, phone, membership, total_spending)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["customer_id"]),
                row.get("first_name", ""),
                row.get("last_name", ""),
                row.get("email", ""),
                row.get("phone_number", ""),
                row.get("membership_status", "Basic"),
                float(row.get("total_spent", 0)),
            ))

    conn.commit()
    conn.close()
