import os
import sys
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uvicorn

# 確保能引用到父目錄的模組
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from groups.group_service import GroupService
from personal.personal_service import PersonalService
from shared.models import TransactionStatus, TransactionType

app = FastAPI(title="Group Ledger API", description="行動端同步伺服器")

# 資料庫路徑設定
DB_PATH = os.path.join(PROJECT_ROOT, "shared", "data", "accounting.db")

# 初始化服務層
group_service = GroupService(DB_PATH)
personal_service = PersonalService(DB_PATH)

# --- 資料模型 (Pydantic Models) ---

class TransactionProposal(BaseModel):
    transaction_id: str
    payer_id: str
    amount: float
    participants: List[str]
    group_id: str
    custom_splits: Optional[Dict[str, float]] = None
    tx_type: str = "EXPENSE"
    description: str = ""
    location: str = ""
    timestamp: Optional[str] = None

class ConfirmRequest(BaseModel):
    user_id: str
    transaction_id: str
    status: Optional[str] = None

# --- API 端點實作 ---

@app.get("/")
async def root():
    return {"message": "Group Ledger API Server is running", "version": "1.0.0"}

# --- 群組相關 ---
@app.get("/api/user/{user_id}/groups")
async def get_user_groups(user_id: str):
    return group_service.get_user_groups(user_id)

@app.get("/api/group/{group_id}/members")
async def get_group_members(group_id: str):
    return group_service.get_group_members(group_id)

@app.get("/api/group/{group_id}/transactions")
async def get_group_transactions(group_id: str):
    return group_service.get_group_transactions(group_id)

@app.get("/api/group/{group_id}/balances")
async def get_group_balances(group_id: str):
    return group_service.get_group_balances(group_id)

# --- 交易相關 ---
@app.post("/api/transaction/propose")
async def propose_transaction(data: TransactionProposal):
    ts = None
    if data.timestamp:
        try: ts = datetime.fromisoformat(data.timestamp)
        except: pass
    
    success = group_service.propose_transaction(
        data.transaction_id, data.payer_id, data.amount, data.participants,
        data.group_id, data.custom_splits, data.tx_type, data.description, 
        data.location, ts
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to propose transaction")
    return {"success": True}

@app.post("/api/transaction/confirm")
async def confirm_transaction(data: ConfirmRequest):
    success = group_service.confirm_transaction(data.user_id, data.transaction_id, data.status)
    return {"success": success}

@app.get("/api/transaction/{tx_id}/details")
async def get_transaction_details(tx_id: str):
    details = group_service.get_transaction_details(tx_id)
    if not details:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return details

# --- 個人中心與好友 ---
@app.get("/api/user/{user_id}/summary")
async def get_user_summary(user_id: str):
    return {"user_id": user_id, "status": "active"}

@app.get("/api/user/{user_id}/history")
async def get_user_history(user_id: str):
    return personal_service.get_personal_history(user_id)

def get_local_ip():
    import socket
    try:
        # 建立一個測試連路以取得主要網路卡 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("\n" + "="*50)
    print("   Group Ledger 行動端伺服器已啟動")
    print(f"   [電腦本機] 請連線至: http://localhost:8000")
    print(f"   [同網域手機/筆電] 請連線至: http://{local_ip}:8000/mobile")
    print("="*50 + "\n")
    
    # 監聽 0.0.0.0 允許同網域下各裝置存取
    uvicorn.run(app, host="0.0.0.0", port=8000)
