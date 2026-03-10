import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'crane_mms.db')
print(f"Connecting to: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET login_phone='13800138000' WHERE contact_phone='13800138000'")
    conn.commit()
    print(f"Updated {cursor.rowcount} rows.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
