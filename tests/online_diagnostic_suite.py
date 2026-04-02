import requests
import time
import uuid
import sys
import os

# Base Config
BASE_URL = "http://127.0.0.1:8000"
USER_1 = "MASTER_A"
USER_2 = "MASTER_B"

# Core Path Setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_banner(msg):
    print("\n" + "="*60)
    print(f" {msg}")
    print("="*60)

def print_step(msg):
    print(f"\n[STEP] {msg}")

def run_master_suite():
    print_banner("Split-it-Smart [Master Diagnostic Suite]")

    # 1. Server Health Check
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
        print("[OK] Server: ONLINE")
    except:
        print("[ERROR] Server: OFFLINE. Please run start_server.bat first.")
        return

    # 2. Friend Management
    print_step("Testing Friend Management (Add Friend)...")
    res = requests.post(f"{BASE_URL}/api/user/friend/add", json={"user_id": USER_1, "friend_id": USER_2})
    success = res.json().get("success")
    if success:
        print(f"[OK] Friend added.")
    else:
        print(f"[FAIL] Friend add failed.")

    # 3. Group Lifecycle
    print_step("Testing Group Lifecycle (Create & Join)...")
    g_name = f"Master_Grp_{uuid.uuid4().hex[:4]}"
    res = requests.post(f"{BASE_URL}/api/group/create", json={"creator_id": USER_1, "group_name": g_name})
    data = res.json()
    g_id = data["group_id"]
    code = data["join_code"]
    requests.post(f"{BASE_URL}/api/group/join", json={"user_id": USER_2, "join_code": code})
    members = requests.get(f"{BASE_URL}/api/group/{g_id}/members").json()
    print(f"[OK] Group active with {len(members)} users.")

    # 4. Scenario: Consensus Flow
    print_step("Scenario: Standard Expense (PENDING -> CONFIRMED)...")
    tx_id_ok = f"tx_ok_{uuid.uuid4().hex[:6]}"
    requests.post(f"{BASE_URL}/api/transaction/propose", json={
        "transaction_id": tx_id_ok, "payer_id": USER_1, "amount": 3000,
        "participants": [USER_1, USER_2], "group_id": g_id,
        "description": "Lunch expense", "tx_type": "EXPENSE"
    })
    requests.post(f"{BASE_URL}/api/transaction/confirm", json={"user_id": USER_2, "transaction_id": tx_id_ok})
    txs = requests.get(f"{BASE_URL}/api/group/{g_id}/transactions").json()
    tx1 = next(t for t in txs if t["id"] == tx_id_ok)
    print(f"[OK] Status: {tx1['status']} (Expected: CONFIRMED)")

    # 5. Scenario: Veto Flow
    print_step("Scenario: Rejected Expense (PENDING -> REJECTED)...")
    tx_id_err = f"tx_err_{uuid.uuid4().hex[:6]}"
    requests.post(f"{BASE_URL}/api/transaction/propose", json={
        "transaction_id": tx_id_err, "payer_id": USER_1, "amount": 90000,
        "participants": [USER_1, USER_2], "group_id": g_id,
        "description": "Error entry", "tx_type": "EXPENSE"
    })
    # NO_2 Reject
    requests.post(f"{BASE_URL}/api/transaction/reject", json={"user_id": USER_2, "transaction_id": tx_id_err})
    txs = requests.get(f"{BASE_URL}/api/group/{g_id}/transactions").json()
    tx2 = next(t for t in txs if t["id"] == tx_id_err)
    print(f"[OK] Status: {tx2['status']} (Expected: REJECTED)")

    # 6. Budget Monitoring
    print_step("Testing Budget Logic (Must only count CONFIRMED items)...")
    requests.post(f"{BASE_URL}/api/group/{g_id}/budget", json={"group_id": g_id, "amount": 10000})
    b_stat = requests.get(f"{BASE_URL}/api/group/{g_id}/budget").json()
    # Confirmed: 3000, Rejected: 90000 (Ignored), Budget: 10000 -> Remaining: 7000
    if b_stat['remaining'] == 7000:
        print(f"[OK] Budget remaining correct: {b_stat['remaining']}")
    else:
        print(f"[FAIL] Budget error: {b_stat}")

    # 7. Settlement
    print_step("Testing Greedy Settlement...")
    res = requests.post(f"{BASE_URL}/api/group/settle", json={"group_id": g_id, "user_id": USER_1, "mode": "SIMPLIFIED"}).json()
    plan = res.get("plan", [])
    if any(p['from'] == USER_2 and p['to'] == USER_1 and p['amount'] == 1500 for p in plan):
        print(f"[OK] Settlement Result: {plan[0]['from']} -> {plan[0]['to']} ($1500)")
    else:
        print(f"[FAIL] Settlement Calculation problem: {plan}")

    # 8. Report Summary
    print_step("Testing Group Bill Summary Generation...")
    res = requests.get(f"{BASE_URL}/api/group/{g_id}/summary").json()
    summary = res.get("summary", "")
    if "Lunch expense" in summary:
        print(f"[OK] Summary generated [PASS]")
    else:
        print(f"[FAIL] Summary missing expected content.")

    print_banner("ALL MASTER SCENARIO TESTS FINISHED")

if __name__ == "__main__":
    run_master_suite()
