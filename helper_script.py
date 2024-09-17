import sqlite3
from hashlib import sha256

def create_tables():
    conn = sqlite3.connect('pizza.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        status TEXT,
        discount_applied BOOLEAN,
        total_price REAL,
        FOREIGN KEY (customer_id) REFERENCES Users(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItems (
        order_id INTEGER,
        item_type TEXT,
        item_id INTEGER,
        quantity INTEGER,
        PRIMARY KEY (order_id, item_type, item_id),
        FOREIGN KEY (order_id) REFERENCES Orders(id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()