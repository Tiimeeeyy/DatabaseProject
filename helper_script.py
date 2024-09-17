import sqlite3

def update_schema():
    conn = sqlite3.connect('pizza.db')
    cursor = conn.cursor()

    # Add the password_hash column if it doesn't exist
    cursor.execute('''
    ALTER TABLE Customers ADD COLUMN password_hash BLOB
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_schema()