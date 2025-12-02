import os
import sys
import base64
from functools import wraps

from flask import Flask, request, jsonify, Response

# --- Добавляем корень проекта в PYTHONPATH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.connection import get_connection, init_db
from utils.hashing import hash_password, verify_password
from utils.validation import is_valid_email, not_empty

# --- Flask-приложение ---
app = Flask(__name__)

# --- Basic Auth (Session 3) ---
BASIC_USER = "staff"
BASIC_PASS = "BCLyon2024"


def _check_basic_auth():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Basic "):
        return False

    try:
        encoded = auth_header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, _, password = decoded.partition(":")
    except Exception:
        return False

    return username == BASIC_USER and password == BASIC_PASS


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Можно пропускать preflight / OPTIONS
        if request.method == "OPTIONS":
            return fn(*args, **kwargs)

        if not _check_basic_auth():
            return Response(
                "Unauthorized",
                status=401,
                headers={"WWW-Authenticate": 'Basic realm="BCL API"'},
            )
        return fn(*args, **kwargs)

    return wrapper


# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ---


@app.before_request
def setup_once():
    if not hasattr(app, "_db_init_done"):
        init_db()
        app._db_init_done = True


# ======================================================================
# =========================  USERS (Session 4)  ========================
# ======================================================================

@app.post("/api/register")
def register():
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    mailing_list = 1 if data.get("mailing_list") else 0
    secret_question = data.get("secret_question", "")
    secret_answer = data.get("secret_answer", "")

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password too short"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return jsonify({"error": "User exists"}), 400

    pwd_hash = hash_password(password)
    sec_hash = hash_password(secret_answer) if secret_answer else None

    cur.execute(
        """
        INSERT INTO users(email, password_hash, first_name, last_name,
                          mailing_list, secret_question, secret_answer_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (email, pwd_hash, first_name, last_name, mailing_list, secret_question, sec_hash),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    return jsonify({"id": user_id, "email": email}), 201


@app.post("/api/login")
def login():
    data = request.json or {}
    email = data.get("email", "")
    password = data.get("password", "")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if not row or not verify_password(password, row["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"user_id": row["id"]})


@app.get("/api/profile")
def profile():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, email, first_name, last_name, phone, mailing_list,
               preferred_delivery, profile_image
        FROM users WHERE id = ?
        """,
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "User not found"}), 404

    return jsonify(dict(row))


@app.put("/api/profile")
def update_profile():
    data = request.json or {}
    user_id = data.get("id")

    if not user_id:
        return jsonify({"error": "id required"}), 400

    fields = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "mailing_list",
        "preferred_delivery",
        "profile_image",
    ]
    updates = []
    values = []

    for f in fields:
        if f in data:
            updates.append(f"{f} = ?")
            values.append(data[f])

    if not updates:
        return jsonify({"error": "nothing to update"}), 400

    values.append(user_id)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# ======================================================================
# =====================  HELPERS: PRODUCTS / ORDERS  ===================
# ======================================================================

def row_get(row, key, default=None):
    """Безопасное получение поля из sqlite3.Row (без .get())."""
    keys = row.keys()
    if key in keys:
        return row[key]
    return default


def row_to_product(row):
    """
    Преобразует строку products в JSON-формат API Session 3.
    Ожидается схема:
        id, product_id, product_name, category, ingredients,
        price, cost, seasonal, active, introduced_date, stock
    """
    return {
        "id": row["id"],
        "product_id": row_get(row, "product_id"),
        "name": row_get(row, "product_name"),
        "category": row_get(row, "category"),
        "price": row_get(row, "price"),
        "cost": row_get(row, "cost"),
        "description": row_get(row, "ingredients"),
        "seasonal": bool(row_get(row, "seasonal", 0)),
        "active": bool(row_get(row, "active", 1)),
        "introduced_date": row_get(row, "introduced_date"),
        "stock": row_get(row, "stock", 0),
    }


# ======================================================================
# =========================  PRODUCTS (Session 3)  =====================
# ======================================================================

@app.get("/api/products")
@require_auth
def list_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()

    data = [row_to_product(r) for r in rows]
    return jsonify(data)


@app.get("/api/products/<int:pid>")
@require_auth
def get_product(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id = ?", (pid,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "not found"}), 404

    return jsonify(row_to_product(row))


@app.post("/api/products")
@require_auth
def create_product():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    category = (data.get("category") or "").strip()
    price = data.get("price")
    cost = data.get("cost")
    description = (data.get("description") or "").strip()
    seasonal = bool(data.get("seasonal"))
    active = bool(data.get("active", True))
    introduced_date = (data.get("introduced_date") or "").strip()

    # Валидации как в Session 3
    if not name or len(name) > 100:
        return jsonify({"error": "ProductName is required and must be <= 100 chars"}), 400
    if not category:
        return jsonify({"error": "Category is required"}), 400

    try:
        price = float(price)
        cost = float(cost)
    except (TypeError, ValueError):
        return jsonify({"error": "Price and Cost must be numeric"}), 400

    if price <= 0:
        return jsonify({"error": "Price must be positive"}), 400
    if cost <= 0 or cost >= price:
        return jsonify({"error": "Cost must be positive and less than Price"}), 400
    if not introduced_date:
        return jsonify({"error": "IntroducedDate is required"}), 400

    stock = int(data.get("stock", 50))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO products(product_id, product_name, category,
                             ingredients, price, cost, seasonal,
                             active, introduced_date, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("product_id"),
            name,
            category,
            description,
            price,
            cost,
            1 if seasonal else 0,
            1 if active else 0,
            introduced_date,
            stock,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.execute("SELECT * FROM products WHERE id = ?", (new_id,))
    row = cur.fetchone()
    conn.close()

    return jsonify(row_to_product(row)), 201


@app.put("/api/products/<int:pid>")
@require_auth
def update_product(pid):
    data = request.json or {}

    # Раскладка: JSON-поля -> колонки
    mapping = {
        "name": "product_name",
        "category": "category",
        "price": "price",
        "cost": "cost",
        "description": "ingredients",
        "seasonal": "seasonal",
        "active": "active",
        "introduced_date": "introduced_date",
        "stock": "stock",
    }

    updates = []
    values = []

    for json_field, col_name in mapping.items():
        if json_field in data:
            val = data[json_field]
            if json_field in ("seasonal", "active"):
                val = 1 if bool(val) else 0
            updates.append(f"{col_name} = ?")
            values.append(val)

    if not updates:
        return jsonify({"error": "nothing to update"}), 400

    values.append(pid)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM products WHERE id = ?", (pid,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "not found"}), 404

    cur.execute(f"UPDATE products SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()

    cur.execute("SELECT * FROM products WHERE id = ?", (pid,))
    row = cur.fetchone()
    conn.close()

    return jsonify(row_to_product(row))


@app.delete("/api/products/<int:pid>")
@require_auth
def delete_product(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM products WHERE id = ?", (pid,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "not found"}), 404

    cur.execute("DELETE FROM products WHERE id = ?", (pid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


# ======================================================================
# =========================  CUSTOMERS (Session 3)  ====================
# ======================================================================

@app.get("/api/customers")
@require_auth
def list_customers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers")
    rows = cur.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append(
            {
                "id": r["id"],
                "customer_id": row_get(r, "customer_id"),
                "name": row_get(r, "name"),
                "gender": row_get(r, "gender"),
                "age": row_get(r, "age"),
                "loyalty_status": row_get(r, "loyalty_status"),
                "total_spent": row_get(r, "total_spent"),
                "churn_status": row_get(r, "churn_status"),
            }
        )
    return jsonify(data)


@app.get("/api/customers/<int:cid>")
@require_auth
def get_customer(cid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id = ?", (cid,))
    r = cur.fetchone()
    conn.close()

    if not r:
        return jsonify({"error": "not found"}), 404

    data = {
        "id": r["id"],
        "customer_id": row_get(r, "customer_id"),
        "name": row_get(r, "name"),
        "gender": row_get(r, "gender"),
        "age": row_get(r, "age"),
        "loyalty_status": row_get(r, "loyalty_status"),
        "total_spent": row_get(r, "total_spent"),
        "churn_status": row_get(r, "churn_status"),
    }
    return jsonify(data)


@app.post("/api/customers")
@require_auth
def create_customer():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO customers(customer_id, name, gender, age,
                              loyalty_status, total_spent, churn_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("customer_id"),
            name,
            data.get("gender"),
            data.get("age"),
            data.get("loyalty_status"),
            data.get("total_spent", 0),
            data.get("churn_status"),
        ),
    )
    conn.commit()
    cid = cur.lastrowid
    cur.execute("SELECT * FROM customers WHERE id = ?", (cid,))
    r = cur.fetchone()
    conn.close()

    return jsonify(
        {
            "id": r["id"],
            "customer_id": row_get(r, "customer_id"),
            "name": row_get(r, "name"),
            "gender": row_get(r, "gender"),
            "age": row_get(r, "age"),
            "loyalty_status": row_get(r, "loyalty_status"),
            "total_spent": row_get(r, "total_spent"),
            "churn_status": row_get(r, "churn_status"),
        }
    ), 201


@app.put("/api/customers/<int:cid>")
@require_auth
def update_customer(cid):
    data = request.json or {}

    mapping = {
        "customer_id": "customer_id",
        "name": "name",
        "gender": "gender",
        "age": "age",
        "loyalty_status": "loyalty_status",
        "total_spent": "total_spent",
        "churn_status": "churn_status",
    }

    updates = []
    values = []
    for json_field, col_name in mapping.items():
        if json_field in data:
            updates.append(f"{col_name} = ?")
            values.append(data[json_field])

    if not updates:
        return jsonify({"error": "nothing to update"}), 400

    values.append(cid)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM customers WHERE id = ?", (cid,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "not found"}), 404

    cur.execute(f"UPDATE customers SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


# ======================================================================
# ==========================  ORDERS (Session 3)  ======================
# ======================================================================

@app.get("/api/orders")
@require_auth
def list_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT o.id,
               o.order_date,
               o.total_amount,
               o.status,
               c.name AS customer_name
        FROM orders o
        LEFT JOIN customers c ON c.id = o.customer_id
        ORDER BY o.id
        """
    )
    rows = cur.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append(
            {
                "id": r["id"],
                "order_date": r["order_date"],
                "total_amount": r["total_amount"],
                "status": r["status"],
                "customer_name": r["customer_name"],
            }
        )
    return jsonify(data)


@app.get("/api/orders/<int:oid>")
@require_auth
def get_order(oid):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT o.id,
               o.order_date,
               o.total_amount,
               o.status,
               c.name AS customer_name
        FROM orders o
        LEFT JOIN customers c ON c.id = o.customer_id
        WHERE o.id = ?
        """,
        (oid,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    cur.execute(
        """
        SELECT oi.id,
               oi.product_id,
               p.product_name AS product_name,
               oi.quantity,
               oi.price AS unit_price
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id = ?
        """,
        (oid,),
    )
    items = [dict(r) for r in cur.fetchall()]
    conn.close()

    data = dict(row)
    data["items"] = items
    return jsonify(data)


@app.post("/api/orders")
@require_auth
def create_order():
    """
    JSON:
    {
      "customer_id": <id customers.id>,
      "items": [
        {"product_id": <id products.id>, "quantity": 2},
        ...
      ]
    }
    """
    data = request.json or {}
    customer_id = data.get("customer_id")
    items = data.get("items", [])

    if not customer_id:
        return jsonify({"error": "customer_id required"}), 400
    if not items:
        return jsonify({"error": "items list is empty"}), 400

    conn = get_connection()
    cur = conn.cursor()

    # Проверка покупателя
    cur.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "customer does not exist"}), 404

    # Проверка продуктов + stock
    product_map = {}
    for it in items:
        pid = it.get("product_id")
        qty = it.get("quantity", 0)

        if not pid or qty <= 0:
            conn.close()
            return jsonify({"error": "invalid product_id or quantity"}), 400

        cur.execute("SELECT id, price, stock FROM products WHERE id = ?", (pid,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": f"product_id {pid} not found"}), 404

        if row["stock"] < qty:
            conn.close()
            return jsonify({"error": f"not enough stock for product {pid}"}), 400

        product_map[pid] = row

    # Создаём заказ
    from datetime import datetime

    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_amount = sum(product_map[i["product_id"]]["price"] * i["quantity"] for i in items)

    cur.execute(
        """
        INSERT INTO orders(customer_id, order_date, total_amount, status)
        VALUES (?, ?, ?, ?)
        """,
        (customer_id, order_date, total_amount, "Pending"),
    )
    order_id = cur.lastrowid

    # Позиции заказа + изменение stock
    for it in items:
        pid = it["product_id"]
        qty = it["quantity"]
        price = product_map[pid]["price"]

        cur.execute(
            """
            INSERT INTO order_items(order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, pid, qty, price),
        )

        cur.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (qty, pid),
        )

    conn.commit()
    conn.close()

    return jsonify({"order_id": order_id, "status": "Pending"}), 201


@app.put("/api/orders/<int:oid>/processing")
@require_auth
def processing_order(oid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = 'Processing' WHERE id = ?", (oid,))
    if cur.rowcount == 0:
        conn.close()
        return jsonify({"error": "Order not found"}), 404
    conn.commit()
    conn.close()
    return jsonify({"status": "Processing"})


@app.put("/api/orders/<int:oid>/complete")
@require_auth
def complete_order(oid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = 'Completed' WHERE id = ?", (oid,))
    if cur.rowcount == 0:
        conn.close()
        return jsonify({"error": "Order not found"}), 404
    conn.commit()
    conn.close()
    return jsonify({"status": "Completed"})


@app.put("/api/orders/<int:oid>/cancel")
@require_auth
def cancel_order(oid):
    """
    Session 3 Acceptance Tests:
    - отмена заказа помечает статус 'Cancelled'
    - ВОССТАНАВЛИВАЕТ запасы (stock) по позициям заказа
    """
    conn = get_connection()
    cur = conn.cursor()

    # Сначала смотрим текущий статус
    cur.execute("SELECT status FROM orders WHERE id = ?", (oid,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    current_status = row["status"]
    if current_status == "Cancelled":
        conn.close()
        return jsonify({"status": "AlreadyCancelled"}), 200

    # Получаем позиции заказа
    cur.execute(
        "SELECT product_id, quantity FROM order_items WHERE order_id = ?",
        (oid,),
    )
    items = cur.fetchall()

    # Восстанавливаем stock
    for it in items:
        cur.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (it["quantity"], it["product_id"]),
        )

    # Меняем статус
    cur.execute("UPDATE orders SET status = 'Cancelled' WHERE id = ?", (oid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "Cancelled"})


# ======================================================================
# =====================  Promotions & Loyalty (S5)  ====================
# ======================================================================

@app.get("/api/promotions")
@require_auth
def list_promotions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM promotions")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.post("/api/promotions")
@require_auth
def create_promotion():
    data = request.json or {}
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO promotions(name, discount_type, discount_value,
                               start_date, end_date, min_order_value, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("name", ""),
            data.get("discount_type", "percent"),
            float(data.get("discount_value", 0)),
            data.get("start_date", ""),
            data.get("end_date", ""),
            data.get("min_order_value"),
            int(data.get("priority", 1)),
        ),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()

    return jsonify({"id": pid}), 201


@app.get("/api/loyalty/<int:cid>")
@require_auth
def get_loyalty(cid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM loyalty WHERE customer_id = ?", (cid,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"customer_id": cid, "points": 0})

    return jsonify(dict(row))


@app.put("/api/loyalty/<int:cid>")
@require_auth
def update_loyalty(cid):
    data = request.json or {}
    points = int(data.get("points", 0))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO loyalty(customer_id, points) VALUES(?, ?)
        ON CONFLICT(customer_id) DO UPDATE SET points = excluded.points
        """,
        (cid, points),
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# ======================================================================
# ==============================  RUN  =================================
# ======================================================================

if __name__ == "__main__":
    init_db()
    print(">>> Server running on http://127.0.0.1:5000")
    app.run(debug=True)
