import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "support.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)

    # Return rows like dictionaries
    connection.row_factory = sqlite3.Row

    # Enable foreign keys
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_database():

    connection = get_connection()

    cursor = connection.cursor()

    # ============================================
    # CUSTOMERS
    # ============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ============================================
    # PAYMENT ACCOUNTS
    # ============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_accounts (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            last_four TEXT NOT NULL,

            FOREIGN KEY (customer_id)
                REFERENCES customers(id)
        )
    """)

    # ============================================
    # ORDERS
    # ============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id TEXT NOT NULL,

            status TEXT NOT NULL,

            total_amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (customer_id)
                REFERENCES customers(id)
        )
    """)

    # ============================================
    # ORDER ITEMS
    # ============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,

            product_name TEXT NOT NULL,

            quantity INTEGER NOT NULL,

            unit_price REAL NOT NULL,

            FOREIGN KEY (order_id)
                REFERENCES orders(id)
        )
    """)

    # ============================================
    # REFUNDS
    # ============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refunds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,

            customer_id TEXT NOT NULL,

            amount REAL NOT NULL,

            status TEXT NOT NULL,

            reason TEXT,

            requested_at TEXT DEFAULT CURRENT_TIMESTAMP,

            processed_at TEXT,

            FOREIGN KEY (order_id)
                REFERENCES orders(id),

            FOREIGN KEY (customer_id)
                REFERENCES customers(id)
        )
    """)

    # ============================================
    # REFUND TRANSACTIONS
    # ============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refund_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            refund_id INTEGER NOT NULL,

            payment_account_id TEXT NOT NULL,

            transaction_reference TEXT UNIQUE NOT NULL,

            amount REAL NOT NULL,

            status TEXT NOT NULL,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (refund_id)
                REFERENCES refunds(id),

            FOREIGN KEY (payment_account_id)
                REFERENCES payment_accounts(id)
        )
    """)

    connection.commit()

    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully.")