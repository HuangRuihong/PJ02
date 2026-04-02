from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import sys

# 將專案根目錄加入路徑，以便導入 backend 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.core.main import DebtSystem

app = FastAPI(title="group ledger 中央同步伺服器")

# 初始化中央資料庫 (位於伺服器端)
db_path = os.path.join("backend", "data", "server_accounting.db")
system = DebtSystem(db_path=db_path)

# --- 模型定義 ---
class CreateGroupRequest(BaseModel):
    creator_id: str
    group_name: str

class JoinGroupRequest(BaseModel):
    user_id: str
    join_code: str

class ProposeTxRequest(BaseModel):
    transaction_id: str
    payer_id: str
    amount: float
    participants: List[str]
    group_id: str
    custom_splits: Optional[Dict[str, float]] = None
    tx_type: str = "EXPENSE"
    description: str = ""
    location: str = ""
    timestamp: Optional[str] = None # ISO format string

class ConfirmTxRequest(BaseModel):
    user_id: str
    transaction_id: str
    status: Optional[str] = None

class SettleDebtsRequest(BaseModel):
    group_id: str
    user_id: str
    mode: str = "ORIGINAL"

class FriendRequest(BaseModel):
    user_id: str
    friend_id: str

class RejectTxRequest(BaseModel):
    user_id: str
    transaction_id: str

class SettleSpecificRequest(BaseModel):
    debtor_id: str
    creditor_id: str
    tx_ids: List[str]

class BudgetRequest(BaseModel):
    group_id: str
    amount: int

class RepayTxRequest(BaseModel):
    group_id: str
    tx_id: str
    debtor_id: str
    creditor_id: str
    amount: float

# --- API 路由 ---

@app.get("/")
def read_root():
    return {"status": "online", "message": "group ledger 中央伺服器已啟動"}

# 群組相關
@app.post("/api/group/create")
def create_group(req: CreateGroupRequest):
    gid, code = system.create_group_with_code(req.creator_id, req.group_name)
    if not gid: raise HTTPException(status_code=500, detail="群組建立失敗")
    return {"group_id": gid, "join_code": code}

@app.post("/api/group/join")
def join_group(req: JoinGroupRequest):
    success = system.join_group_by_code(req.user_id, req.join_code)
    return {"success": success}

@app.get("/api/user/{user_id}/groups")
def get_user_groups(user_id: str):
    return system.get_user_groups(user_id)

@app.get("/api/group/{group_id}/members")
def get_group_members(group_id: str):
    return system.get_group_members(group_id)

# 交易相關
@app.post("/api/transaction/propose")
def propose_tx(req: ProposeTxRequest):
    # 處理時間戳字符串轉 datetime (若有)
    from datetime import datetime
    ts = datetime.fromisoformat(req.timestamp) if req.timestamp else None
    success = system.propose_transaction(
        req.transaction_id, req.payer_id, req.amount, req.participants, 
        req.group_id, req.custom_splits, req.tx_type, req.description, req.location, ts
    )
    return {"success": success}

@app.post("/api/transaction/confirm")
def confirm_tx(req: ConfirmTxRequest):
    success = system.confirm_transaction(req.user_id, req.transaction_id, req.status)
    return {"success": success}

@app.post("/api/transaction/reject")
def reject_tx(req: RejectTxRequest):
    # 如果後端有實作 reject_transaction 則呼叫，否則回傳 False
    if hasattr(system, "reject_transaction"):
        success = system.reject_transaction(req.user_id, req.transaction_id)
        return {"success": success}
    return {"success": False}

@app.post("/api/transaction/settle_specific")
def settle_specific(req: SettleSpecificRequest):
    success = system.settle_specific_debts(req.debtor_id, req.creditor_id, req.tx_ids)
    return {"success": success}

@app.get("/api/group/{group_id}/transactions")
def get_group_txs(group_id: str):
    return system.get_group_transactions(group_id)

@app.get("/api/group/{group_id}/budget")
def get_group_budget_status(group_id: str):
    return system.get_group_budget_status(group_id)

@app.post("/api/group/{group_id}/budget")
def set_group_budget(group_id: str, req: BudgetRequest):
    success = system.set_group_budget(group_id, req.amount)
    return {"success": success}

@app.get("/api/group/{group_id}/summary")
def get_group_summary(group_id: str):
    return {"summary": system.generate_group_bill_summary(group_id)}

@app.delete("/api/group/{group_id}")
def delete_group(group_id: str):
    success = system.delete_group(group_id)
    return {"success": success}

@app.get("/api/group/{group_id}/balances")
def get_group_balances(group_id: str):
    return system.get_group_balances(group_id)

@app.post("/api/group/settle")
def settle_debts(req: SettleDebtsRequest):
    plan = system.settle_debts(req.group_id, req.user_id, req.mode)
    return {"plan": plan}

# 個人相關
@app.get("/api/user/{user_id}/debts")
def get_personal_debts(user_id: str):
    payables, receivables = system.get_personal_debts(user_id)
    return {"payables": payables, "receivables": receivables}

@app.get("/api/user/{user_id}/summary")
def get_user_summary(user_id: str):
    return system.get_user_summary(user_id)

@app.get("/api/user/{user_id}/friends")
def get_user_friends(user_id: str):
    # 若有 get_friends 則呼叫
    if hasattr(system, "get_friends"):
        return system.get_friends(user_id)
    return []

@app.post("/api/user/friend/add")
def add_friend(req: FriendRequest):
    if hasattr(system, "add_friend"):
        success = system.add_friend(req.user_id, req.friend_id)
        return {"success": success}
    return {"success": False}

@app.get("/api/system/overdue")
def check_overdue():
    return system.check_overdue_transactions()

@app.get("/api/user/{user_id}/history")
def get_personal_history(user_id: str):
    return system.get_personal_history(user_id)

# 工具相關
@app.get("/api/transaction/{tx_id}/details")
def get_tx_details(tx_id: str):
    return system.get_transaction_details(tx_id)

@app.delete("/api/transaction/{tx_id}")
def delete_tx(tx_id: str):
    success = system.delete_transaction(tx_id)
    return {"success": success}

@app.post("/api/transaction/repay")
def repay_tx(req: RepayTxRequest):
    success = system.repay_transaction(req.group_id, req.tx_id, req.debtor_id, req.creditor_id, req.amount)
    return {"success": success}

@app.get("/api/transaction/{tx_id}/notification")
def get_notification(tx_id: str):
    return {"message": system.get_notification_message(tx_id)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
