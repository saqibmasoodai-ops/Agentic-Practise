from database import get_connection, create_database


def seed_database():

    # Make sure tables exist
    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    # ============================================================
    # CUSTOMERS
    # ============================================================

    customers = [
        (
            "cust_001",
            "Saqib",
            "saqib@example.com"
        ),

        (
            "cust_002",
            "Ali",
            "ali@example.com"
        ),
    ]

    for customer in customers:

        cursor.execute("""
            INSERT OR IGNORE INTO customers
            (
                id,
                name,
                email
            )
            VALUES (?, ?, ?)
        """, customer)

    # ============================================================
    # PAYMENT ACCOUNTS
    # ============================================================

    payment_accounts = [

        (
            "pay_001",
            "cust_001",
            "stripe",
            "4242"
        ),

        (
            "pay_002",
            "cust_002",
            "stripe",
            "1111"
        ),
    ]

    for account in payment_accounts:

        cursor.execute("""
            INSERT OR IGNORE INTO payment_accounts
            (
                id,
                customer_id,
                provider,
                last_four
            )
            VALUES (?, ?, ?, ?)
        """, account)

    # ============================================================
    # ORDERS
    # ============================================================

    orders = [

        # Saqib's orders
        (
            1,
            "cust_001",
            "delivered",
            10.99
        ),

        (
            2,
            "cust_001",
            "delivered",
            22.00
        ),

        (
            3,
            "cust_001",
            "delivered",
            19.00
        ),

        # Ali's order
        (
            4,
            "cust_002",
            "delivered",
            50.00
        ),
    ]

    for order in orders:

        cursor.execute("""
            INSERT OR IGNORE INTO orders
            (
                id,
                customer_id,
                status,
                total_amount
            )
            VALUES (?, ?, ?, ?)
        """, order)

    # ============================================================
    # ORDER ITEMS
    # ============================================================

    items = [

        (
            1,
            "Keyboard",
            1,
            10.99
        ),

        (
            2,
            "Wireless Mouse",
            1,
            22.00
        ),

        (
            3,
            "USB Cable",
            1,
            19.00
        ),

        (
            4,
            "Mechanical Keyboard",
            1,
            50.00
        ),
    ]

    for order_id, product_name, quantity, unit_price in items:

        cursor.execute("""
            INSERT OR IGNORE INTO order_items
            (
                order_id,
                product_name,
                quantity,
                unit_price
            )
            VALUES (?, ?, ?, ?)
        """, (
            order_id,
            product_name,
            quantity,
            unit_price
        ))

    connection.commit()
    connection.close()

    print("Database seeded successfully.")


if __name__ == "__main__":

    seed_database()