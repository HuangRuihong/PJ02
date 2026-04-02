import sqlite3
import os

DB_PATH = "backend/data/server_accounting.db"

def inspect():
    if not os.path.exists(DB_PATH):
        print("DB not found")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- 檢查交易參與者狀態 ---")
    cursor.execute("SELECT transaction_id, user_id, status FROM transaction_participants WHERE transaction_id LIKE 'tx_err%';")
    rows = cursor.fetchall()
    for r in rows:
        print(f"TX: {r[0]} | User: {r[1]} | Status: {r[2]}")
        
    print("\n--- 檢查交易主表狀態 ---")
    cursor.execute("SELECT transaction_id, status FROM transactions WHERE transaction_id LIKE 'tx_err%';")
    rows = cursor.fetchall()
    for r in rows:
        print(f"TX: {r[0]} | Main Status: {r[1]}")
        
    conn.close()

if __name__ == "__main__":
    inspect()
