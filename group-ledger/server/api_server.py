import uvicorn
import socket
from fastapi import FastAPI, HTTPException, Body, Request
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# 確保能從根目錄導入模組
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client_src_dir = os.path.join(base_dir, "client", "src")
sys.path.append(client_src_dir)

from intelligence.debt_system import DebtSystem
from shared.models import TransactionStatus

# 載入環境變數 (優先讀取伺服器目錄下的 .env)
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

app = FastAPI(title="Group Ledger API Server", version="2.0.0")

# 配置與狀態
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

system = DebtSystem()

# --- 統一 Response 格式 ---

def success_response(data=None):
    return {"success": True, "data": data}

def error_response(code: int, message: str, detail: str = None):
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "detail": detail
        }
    }

# 用於記錄已顯示過連線訊息的 IP，避免重複洗版
logged_ips = set()

def get_local_ip():
    """自動偵測本機於區域網路中的 IP 位址"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 嘗試連接 Google DNS (不會真正送出封包) 以獲取對外 IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

local_ip = get_local_ip()
print("==========================================")
print(f" [Server Mode] Group Ledger API Server")
print("==========================================")
print(f"[Info] Server IP Address : {local_ip}")
print(f"[Info] Client should connect to : http://{local_ip}:{SERVER_PORT}")
print("")
print(f"[Info] Starting API server on port {SERVER_PORT}...")
print(f"[Info] Press Ctrl+C to stop the server.")
print("------------------------------------------")
print(f"[System] 資料庫已就緒: {os.path.abspath(system.db_path)}")
print(f"[System] 等待客戶端連線...")

# --- 資料模型 ---

class TransactionPropose(BaseModel):
    transaction_id: str
    payer_id: str
    amount: float
    participants: List[str]
    group_id: str
    custom_splits: Optional[Dict[str, float]] = None
    tx_type: str = "EXPENSE"
    category: str = "OTHER"
    description: str = ""
    location: str = ""
    timestamp: Optional[datetime] = None

# --- API 端點 ---

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """全局中介軟體：監控所有進入伺服器的連線"""
    client_ip = request.client.host
    # 僅針對第一次連線的 IP 顯示進入訊息，減少負擔
    if client_ip not in logged_ips:
        print(f" >>> [連線進入] 來自 IP: {client_ip} | 歡迎使用者進入系統")
        logged_ips.add(client_ip)
    
    response = await call_next(request)
    return response

@app.get("/")
def read_root():
    return {"status": "online", "message": "Group Ledger API Server is running"}

# --- 群組管理 ---

@app.get("/api/groups/{user_id}")
def get_user_groups(user_id: str):
    return success_response(system.get_user_groups(user_id))

@app.get("/api/group/{group_id}/members")
def get_group_members(group_id: str):
    return success_response(system.get_group_members(group_id))

@app.post("/api/group/join")
def join_group(user_id: str = Body(...), code: str = Body(...)):
    print(f"[Group] 使用者 {user_id} 嘗試加入群組，代碼: {code}")
    if system.join_group_by_code(user_id, code):
        print(f"[Group] 使用者 {user_id} 成功加入群組 {code}")
        return success_response()
    print(f"[Group] 使用者 {user_id} 加入群組失敗")
    raise HTTPException(status_code=400, detail=error_response(400, "Join group failed", f"User {user_id} failed to join group with code {code}"))

@app.post("/api/group/create")
def create_group(user_id: str = Body(...), name: str = Body(...)):
    print(f"[Group] 使用者 {user_id} 正在建立群組: {name}")
    gid, code = system.create_group_with_code(user_id, name)
    if gid:
        print(f"[Group] 群組建立成功！ ID: {gid}, 代碼: {code}")
        return success_response({"group_id": gid, "code": code})
    print(f"[Group] 群組建立失敗")
    raise HTTPException(status_code=500, detail=error_response(500, "Create group failed", f"Failed to create group '{name}' for user {user_id}"))

# --- 交易管理 ---

@app.post("/api/transaction/propose")
def propose_transaction(tx: TransactionPropose):
    print(f"[Transaction] 收到新交易: {tx.description} (金額: {tx.amount}, 付款人: {tx.payer_id}, 群組: {tx.group_id})")
    success = system.propose_transaction(
        tx.transaction_id, tx.payer_id, tx.amount, tx.participants, 
        tx.group_id, tx.custom_splits, tx.tx_type, tx.description, 
        tx.location, tx.timestamp or datetime.now(),
        category=tx.category
    )
    if success:
        print(f"[Transaction] 交易 {tx.transaction_id} 紀錄成功")
        return success_response()
    print(f"[Transaction] 交易紀錄失敗")
    raise HTTPException(status_code=500, detail=error_response(500, "Propose transaction failed"))

@app.post("/api/transaction/confirm")
def confirm_transaction(user_id: str = Body(...), transaction_id: str = Body(...)):
    print(f"[Transaction] 使用者 {user_id} 正在確認交易: {transaction_id}")
    if system.confirm_transaction(user_id, transaction_id):
        print(f"[Transaction] 使用者 {user_id} 確認成功")
        return success_response()
    print(f"[Transaction] 使用者 {user_id} 確認失敗")
    raise HTTPException(status_code=500, detail=error_response(500, "Confirm transaction failed"))

@app.post("/api/transaction/reject")
def reject_transaction(user_id: str = Body(...), transaction_id: str = Body(...)):
    if hasattr(system, "reject_transaction") and system.reject_transaction(user_id, transaction_id):
        return success_response()
    raise HTTPException(status_code=500, detail=error_response(500, "Reject transaction failed"))

@app.get("/api/group/{group_id}/transactions")
def get_group_transactions(group_id: str):
    print(f"[Sync] 正在抓取群組 {group_id} 的交易紀錄...")
    return success_response(system.get_group_transactions(group_id))

@app.get("/api/group/{group_id}/balances")
def get_group_balances(group_id: str):
    return success_response(system.get_group_balances(group_id))

@app.get("/api/transaction/{transaction_id}")
@app.get("/api/transaction/{transaction_id}/details")
def get_transaction_details(transaction_id: str):
    details = system.get_transaction_details(transaction_id)
    if details:
        return success_response(details)
    raise HTTPException(status_code=404, detail=error_response(404, "Transaction not found"))

@app.get("/api/transaction/{transaction_id}/notification")
def get_notification(transaction_id: str):
    msg = system.get_notification_message(transaction_id)
    return success_response({"message": msg})

@app.post("/api/transaction/settle_specific")
def settle_specific(debtor_id: str = Body(...), creditor_id: str = Body(...), tx_ids: List[str] = Body(...)):
    if system.settle_specific_debts(debtor_id, creditor_id, tx_ids):
        return success_response()
    raise HTTPException(status_code=500, detail=error_response(500, "Specific settlement failed"))

@app.delete("/api/transaction/{transaction_id}")
def delete_transaction(transaction_id: str):
    if system.delete_transaction(transaction_id):
        return success_response()
    raise HTTPException(status_code=500, detail=error_response(500, "Delete transaction failed"))

# --- 個人債務與結算 ---

@app.get("/api/user/{user_id}/debts")
def get_personal_debts(user_id: str):
    print(f"[Sync] 使用者 {user_id} 正在請求個人債務清單 (應收/應付)...")
    payables, receivables = system.get_personal_debts(user_id)
    return success_response({"payables": payables, "receivables": receivables})

@app.get("/api/user/{user_id}/summary")
def get_user_summary(user_id: str):
    return success_response(system.get_user_summary(user_id))

@app.get("/api/user/{user_id}/history")
def get_personal_history(user_id: str):
    return success_response(system.get_personal_history(user_id))

@app.post("/api/group/settle")
def settle_debts(group_id: str = Body(...), user_id: str = Body(...), mode: str = "ORIGINAL"):
    res = system.settle_debts(group_id, user_id, mode=mode)
    if res:
        return success_response(res)
    raise HTTPException(status_code=500, detail=error_response(500, "Settlement failed"))

@app.post("/api/transaction/repay")
def repay_transaction(group_id: str = Body(...), tx_id: str = Body(...), debtor_id: str = Body(...), creditor_id: str = Body(...), amount: float = Body(...)):
    if system.repay_transaction(group_id, tx_id, debtor_id, creditor_id, amount):
        return success_response()
    raise HTTPException(status_code=500, detail=error_response(500, "Repayment failed"))

@app.post("/api/transaction/request_settlement")
def request_settlement(debtor_id: str = Body(...), creditor_id: str = Body(...), amount: float = Body(...), method: str = Body(...), tx_ids: List[str] = Body(...)):
    if system.request_settlement(debtor_id, creditor_id, amount, method, tx_ids):
        return success_response()
    raise HTTPException(status_code=500, detail=error_response(500, "Repayment request failed"))

# --- 預算與分析 ---


@app.get("/api/group/{group_id}/summary")
def get_group_summary(group_id: str):
    summary = system.generate_group_bill_summary(group_id)
    return success_response({"summary": summary})

@app.get("/api/group/{group_id}/analysis")
def get_group_analysis(group_id: str):
    return success_response(system.get_group_transactions(group_id))

@app.delete("/api/group/{group_id}")
def delete_group(group_id: str):
    if system.delete_group(group_id):
        return success_response()
    raise HTTPException(status_code=500, detail=error_response(500, "Delete group failed"))

# --- 其他功能 ---

@app.get("/api/system/overdue")
def scan_overdue():
    return success_response(system.check_overdue_transactions())

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
