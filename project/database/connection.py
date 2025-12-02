import sqlite3
import os

DB_PATH = "bcl_app.sqlite"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ----------------------- USERS -----------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            mailing_list INTEGER DEFAULT 0,
            preferred_delivery TEXT,
            profile_image TEXT,
            secret_question TEXT,
            secret_answer_hash TEXT
        );
    """)

    # ----------------------- PRODUCTS -----------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            cost REAL,
            description TEXT,
            seasonal INTEGER,
            active INTEGER,
            introduced_date TEXT,
            stock INTEGER DEFAULT 50
        );
    """)

    # ----------------------- CUSTOMERS -----------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            membership TEXT,
            total_spending REAL
        );
    """)

    # ----------------------- ORDERS -----------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_date TEXT,
            total_amount REAL,
            status TEXT DEFAULT 'Pending'
        );
    """)

    # ----------------------- ORDER ITEMS -----------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL
        );
    """)

    # ----------------------- PROMOTIONS -----------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            discount_type TEXT,
            discount_value REAL,
            start_date TEXT,
            end_date TEXT,
            min_order_value REAL,
            priority INTEGER
        );
    """)

    # ----------------------- LOYALTY -----------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loyalty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER UNIQUE,
            points INTEGER DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()

    print("Database schema initialized.")

    # ----------------------- LOAD CLEANED CSV -----------------------
    try:
        from .seed_data import seed_from_csv
        seed_from_csv()
        print("Cleaned CSV imported into the DB.")
    except Exception as e:
        print("Failed to load cleaned CSV:", e)
