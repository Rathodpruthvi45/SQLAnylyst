import sqlite3

DB_PATH = "example.db"

def insert_dummy_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ---------------- USERS ----------------
    users = [
        ("Pruthvi Rathod", "pruthvi@gmail.com", "hashed_pwd_1"),
        ("Amit Sharma", "amit@gmail.com", "hashed_pwd_2"),
        ("Sneha Patil", "sneha@gmail.com", "hashed_pwd_3"),
        ("Rahul Verma", "rahul@gmail.com", "hashed_pwd_4"),
        ("Neha Singh", "neha@gmail.com", "hashed_pwd_5"),
        ("Karan Mehta", "karan@gmail.com", "hashed_pwd_6"),
        ("Pooja Kulkarni", "pooja@gmail.com", "hashed_pwd_7"),
        ("Ankit Jain", "ankit@gmail.com", "hashed_pwd_8"),
        ("Riya Deshmukh", "riya@gmail.com", "hashed_pwd_9"),
        ("Suresh Naik", "suresh@gmail.com", "hashed_pwd_10"),
    ]

    cursor.executemany(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        users
    )

    # ---------------- ORDERS ----------------
    orders = [
        (1, 250.50, "paid"),
        (2, 120.00, "pending"),
        (3, 560.75, "paid"),
        (4, 99.99, "cancelled"),
        (5, 340.20, "paid"),
        (6, 150.00, "pending"),
        (7, 789.99, "paid"),
        (8, 45.50, "cancelled"),
        (9, 999.00, "paid"),
        (10, 220.40, "pending"),
    ]

    cursor.executemany(
        "INSERT INTO orders (user_id, amount, status) VALUES (?, ?, ?)",
        orders
    )

    # ---------------- CONVERSATIONS ----------------
    conversations = [
        (1, "Order status inquiry"),
        (2, "Payment failed"),
        (3, "Account verification"),
        (4, "Refund request"),
        (5, "Delivery delay"),
        (6, "Change address"),
        (7, "Cancel order"),
        (8, "Login issue"),
        (9, "Coupon not applied"),
        (10, "General support"),
    ]

    cursor.executemany(
        "INSERT INTO conversations (user_id, title) VALUES (?, ?)",
        conversations
    )

    # ---------------- MESSAGES ----------------
    messages = [
        (1, "user", "Can you tell me my order status?"),
        (1, "assistant", "Your order has been delivered."),
        (2, "user", "Payment failed but money deducted."),
        (2, "assistant", "We are checking with the bank."),
        (3, "user", "How do I verify my account?"),
        (3, "assistant", "Please click the verification link."),
        (4, "user", "I want a refund."),
        (4, "assistant", "Refund has been initiated."),
        (5, "user", "My order is delayed."),
        (5, "assistant", "We apologize for the inconvenience."),
    ]

    cursor.executemany(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        messages
    )

    conn.commit()
    conn.close()

    print("✅ 10 dummy records inserted into each table successfully.")


if __name__ == "__main__":
    insert_dummy_data()
