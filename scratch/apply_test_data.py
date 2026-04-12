import sqlite3
import os

db_path = r"c:\PJ02\group ledger\shared\data\accounting.db"
sql_path = r"c:\PJ02\group ledger\doc\test_data_seed.sql"

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

try:
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Success: Test data imported successfully.")
except Exception as e:
    print(f"Error: {e}")
