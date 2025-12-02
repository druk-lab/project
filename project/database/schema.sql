PRAGMA foreign_keys = ON;

-- Пользователи (управление, логин, секретный вопрос, рассылка)
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    phone           TEXT,
    mailing_list    INTEGER NOT NULL DEFAULT 0,
    profile_image   TEXT,
    secret_question TEXT,
    secret_answer_hash TEXT,
    preferred_delivery TEXT CHECK(preferred_delivery IN ('Pickup', 'Delivery')) DEFAULT 'Pickup'
);

CREATE TABLE IF NOT EXISTS delivery_addresses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    label       TEXT NOT NULL, -- Дом, Работа и т.п.
    address     TEXT NOT NULL,
    city        TEXT,
    postal_code TEXT,
    country     TEXT,
    is_default  INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Продукты/клиенты/заказы как в Session 3
CREATE TABLE IF NOT EXISTS customers (
    id              INTEGER PRIMARY KEY,
    first_name      TEXT,
    last_name       TEXT,
    email           TEXT,
    phone           TEXT,
    membership      TEXT,
    total_spending  REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    category        TEXT,
    price           REAL NOT NULL,
    cost            REAL NOT NULL,
    description     TEXT,
    seasonal        INTEGER NOT NULL DEFAULT 0,
    active          INTEGER NOT NULL DEFAULT 1,
    introduced_date TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL,
    order_date      TEXT NOT NULL,
    total_amount    REAL NOT NULL,
    status          TEXT NOT NULL CHECK(status IN ('Pending','Processing','Completed','Cancelled')),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL,
    unit_price  REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Promotions и Loyalty (Session 5)
CREATE TABLE IF NOT EXISTS promotions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    discount_type   TEXT NOT NULL CHECK(discount_type IN ('percent','fixed')),
    discount_value  REAL NOT NULL,
    start_date      TEXT NOT NULL,
    end_date        TEXT NOT NULL,
    min_order_value REAL,
    priority        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS promotion_products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    promotion_id    INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS loyalty (
    customer_id     INTEGER PRIMARY KEY,
    points          INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Таблица для токенов/сброса пароля (упрощенно)
CREATE TABLE IF NOT EXISTS password_resets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    created_at  TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
