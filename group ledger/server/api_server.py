import uvicorn
from fastapi import FastAPI, HTTPException, Body
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import os
import sys

# 確保能從根目錄導入模組
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Users"))

from intelligence.debt_system import DebtSystem
from shared.models import TransactionStatus

app = FastAPI(title="Group Ledger API Server", version="2.0.0")
system = DebtSystem()

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

@app.get("/")
def read_root():
    return {"status": "online", "message": "Group Ledger API Server is running"}

# --- 群組管理 ---

@app.get("/api/groups/{user_id}")
def get_user_groups(user_id: str):
    return system.get_user_groups(user_id)

@app.get("/api/group/{group_id}/members")
def get_group_members(group_id: str):
    return system.get_group_members(group_id)

@app.post("/api/group/join")
def join_group(user_id: str = Body(...), code: str = Body(...)):
    if system.join_group_by_code(user_id, code):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Join group failed")

@app.post("/api/group/create")
def create_group(user_id: str = Body(...), name: str = Body(...)):
    gid, code = system.create_group_with_code(user_id, name)
    if gid:
        return {"group_id": gid, "code": code}
    raise HTTPException(status_code=500, detail="Create group failed")

# --- 交易管理 ---

@app.post("/api/transaction/propose")
def propose_transaction(tx: TransactionPropose):
    success = system.propose_transaction(
        tx.transaction_id, tx.payer_id, tx.amount, tx.participants, 
        tx.group_id, tx.custom_splits, tx.tx_type, tx.description, 
        tx.location, tx.timestamp or datetime.now(),
        category=tx.category
    )
    if success:
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Propose transaction failed")

@app.post("/api/transaction/confirm")
def confirm_transaction(user_id: str = Body(...), transaction_id: str = Body(...)):
    if system.confirm_transaction(user_id, transaction_id):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Confirm transaction failed")

@app.post("/api/transaction/reject")
def reject_transaction(user_id: str = Body(...), transaction_id: str = Body(...)):
    if hasattr(system, "reject_transaction") and system.reject_transaction(user_id, transaction_id):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Reject transaction failed")

@app.get("/api/group/{group_id}/transactions")
def get_group_transactions(group_id: str):
    return system.get_group_transactions(group_id)

@app.get("/api/transaction/{transaction_id}")
def get_transaction_details(transaction_id: str):
    details = system.get_transaction_details(transaction_id)
    if details:
        return details
    raise HTTPException(status_code=404, detail="Transaction not found")

# --- 個人債務與結算 ---

@app.get("/api/user/{user_id}/debts")
def get_personal_debts(user_id: str):
    payables, receivables = system.get_personal_debts(user_id)
    return {"payables": payables, "receivables": receivables}

@app.get("/api/user/{user_id}/summary")
def get_user_summary(user_id: str):
    return system.get_user_summary(user_id)

@app.get("/api/user/{user_id}/history")
def get_personal_history(user_id: str):
    return system.get_personal_history(user_id)

@app.post("/api/group/settle")
def settle_debts(group_id: str = Body(...), user_id: str = Body(...), mode: str = "ORIGINAL"):
    if system.settle_debts(group_id, user_id, mode=mode):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Settlement failed")

@app.post("/api/transaction/repay")
def request_repayment(debtor_id: str = Body(...), creditor_id: str = Body(...), amount: float = Body(...), method: str = Body(...), tx_ids: List[str] = Body(...)):
    if system.request_settlement(debtor_id, creditor_id, amount, method, tx_ids):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Repayment request failed")

# --- 其他功能 ---

@app.get("/api/system/overdue")
def scan_overdue():
    return system.check_overdue_transactions()

@app.get("/api/group/{group_id}/analysis")
def get_group_analysis(group_id: str):
    # 這部分邏輯通常在前端 Canvas 繪製，這裡回傳基礎數據
    return system.get_group_transactions(group_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
