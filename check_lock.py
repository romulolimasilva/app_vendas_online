import sqlite3
import time

def check_db_lock():
    try:
        conn = sqlite3.connect('users.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM produto')
        count = cursor.fetchone()[0]
        print(f"Produto count: {count}")
        conn.close()
        print("Database is not locked.")
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("Database is locked.")
        else:
            print(f"Other error: {e}")

if __name__ == "__main__":
    check_db_lock()
