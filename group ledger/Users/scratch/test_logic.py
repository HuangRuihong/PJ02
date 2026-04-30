import os
import sys
import sqlite3
from datetime import datetime
import uuid

# 確保可以匯入專案模組
sys.path.append(os.getcwd())

from intelligence.debt_system import DebtSystem
from shared.models import TransactionStatus

def setup_test_db():
    shared_dir = os.path.join(os.getcwd(), "shared", "data")
    os.makedirs(shared_dir, exist_ok=True)
    db_path = os.path.join(shared_dir, "test_accounting.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 初始化資料庫結構 (模擬系統啟動)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    schema_path = os.path.join(os.getcwd(), "doc", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
    return db_path

def run_integration_test():
    db_path = setup_test_db()
    system = DebtSystem(db_path=db_path)
    
    users = ["87", "88", "89", "90"]
    print("--- Start Integration Test (87, 88, 89, 90) ---")

    # 1. Establish friends
    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            system.add_friend(users[i], users[j])

    # 2. Create Group
    gid, _ = system.create_group_with_code("87", "Graduation Trip")
    for u in ["88", "89", "90"]:
        system.add_member_to_group(gid, u)
    print(f"[Group Created] ID: {gid}")

    # 3. Group Expense: 87 pays $1000 for 4 people.
    # Each person (88, 89, 90) owes 87 $250.
    system.propose_transaction("tx_g1", "87", 1000, users, gid, description="Dinner")
    for u in users: system.confirm_transaction(u, "tx_g1")
    
    # 4. Private Expense: 88 pays $600 just for 87 (Private Buy)
    # We set participants to just ["87"] so 87 owes 88 full $600.
    system.propose_transaction("tx_p1", "88", 600, ["87"], "PERSONAL", description="Private Gift")
    system.confirm_transaction("87", "tx_p1")

    # 5. Verify Cross Balance for 88
    # Group: Owe 87 $250 (-250)
    # Private: 87 owes 88 $600 (+600)
    # Net Balance: +350
    summary_88 = system.get_user_summary("88")
    bal_with_87 = summary_88.get("87", 0)
    print(f"88's balance with 87: ${bal_with_87} (Expected: +350)")
    
    if bal_with_87 == 350:
        print("[PASS] Cross-balance calculation is correct!")
    else:
        print(f"[FAIL] Expected +350, got {bal_with_87}")
        return

    # 6. Test Smart Repayment: 87 repays 88 the balance of $350
    # 87 (debtor) -> 88 (creditor)
    system.request_settlement("87", "88", 350, "Bank Transfer", ["tx_g1", "tx_p1"])
    
    # Find the REPAY_REQUEST ID
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT transaction_id, location FROM transactions WHERE type = 'REPAY_REQUEST' ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        repay_tid = row[0]
        repay_loc = row[1]
    
    print(f"Repayment Request Sent: {repay_tid}, settling: {repay_loc}")
    
    # 88 Confirms Receipt
    system.confirm_transaction("88", repay_tid)
    print("88 confirmed receipt of $350.")

    # 7. Final Verification
    final_summary_88 = system.get_user_summary("88")
    final_bal = final_summary_88.get("87", 0)
    print(f"Final balance between 87 and 88: {final_bal} (Expected: 0)")
    
    # Check if original transactions are SETTLED
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM transaction_participants WHERE transaction_id = ? AND user_id = ?", ("tx_g1", "88"))
        st_g = cursor.fetchone()[0]
        cursor.execute("SELECT status FROM transaction_participants WHERE transaction_id = ? AND user_id = ?", ("tx_p1", "87"))
        st_p = cursor.fetchone()[0]
        cursor.execute("SELECT status FROM transactions WHERE transaction_id = ?", (repay_tid,))
        st_r = cursor.fetchone()[0]
        
    print(f"Status check - Group Item: {st_g}, Private Item: {st_p}, Repay Item: {st_r}")

    if final_bal == 0 and st_g == 'SETTLED' and st_p == 'SETTLED' and st_r == 'SETTLED':
        print("[SUCCESS] Cross-settlement and auto-sync logic fully verified!")
    else:
        print("[FAILED] Logic check failed.")

if __name__ == "__main__":
    run_integration_test()
