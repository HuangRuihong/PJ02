import sqlite3
import os

DB_PATH = "backend/data/server_accounting.db"

def debug():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n--- 檢查 [拒絕交易] 情境 (tx_err%) ---")
    cursor.execute("SELECT transaction_id, user_id, status FROM transaction_participants WHERE transaction_id LIKE 'tx_err%';")
    for r in cursor.fetchall():
        print(f"TP: {r[0]} | User: {r[1]} | Status: {r[2]}")
        
    cursor.execute("SELECT transaction_id, group_id, status FROM transactions WHERE transaction_id LIKE 'tx_err%';")
    for r in cursor.fetchall():
        print(f"TX: {r[0]} | Group: {r[1]} | Main Status: {r[2]}")

    print("\n--- 檢查群組最新 5 筆交易 ---")
    cursor.execute("SELECT transaction_id, description, status FROM transactions ORDER BY timestamp DESC LIMIT 5;")
    for r in cursor.fetchall():
        print(f"ID: {r[0]} | Desc: {r[1]} | Status: {r[2]}")

    conn.close()

if __name__ == "__main__":
    debug()
