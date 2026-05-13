import requests
import json
import time
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import os

from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

class NetworkDebtSystem:
    """
    網路代理類別：將所有原有的數據庫呼叫改寫為 REST API 網路請求。
    它完美替代了本地的 DebtSystem，讓 GUI 無需大規模重規即能聯網。
    """
    def __init__(self, base_url=None):
        # 優先順序：建構子參數 > 環境變數 > 預設值
        url = base_url or os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
        # 自動去除結尾斜線，避免拼接時出現雙斜線 (//api)
        self.base_url = url.rstrip("/")
        self.current_user = None

    def _post(self, path, data, retries=2):
        for i in range(retries + 1):
            try:
                res = requests.post(f"{self.base_url}{path}", json=data, timeout=5)
                res.raise_for_status() # 檢查 HTTP 錯誤狀態碼
                return res.json()
            except Exception as e:
                if i == retries:
                    # 記錄錯誤並回傳結構化錯誤訊息
                    return {"success": False, "error": f"網路連線失敗 (POST {path}): {str(e)}"}
                time.sleep(0.5)

    def _get(self, path, retries=2):
        for i in range(retries + 1):
            try:
                res = requests.get(f"{self.base_url}{path}", timeout=5)
                res.raise_for_status()
                return res.json()
            except Exception as e:
                if i == retries:
                    # 針對 GET 請求，若失敗則回傳帶有錯誤標記的物件
                    error_msg = f"數據獲取失敗 (GET {path}): {str(e)}"
                    if "/groups" in path or "/members" in path:
                        return {"success": False, "error": error_msg, "data": []}
                    return {"success": False, "error": error_msg}
                time.sleep(0.5)

    # --- 群組相關轉發 ---
    def create_group_with_code(self, creator_id, group_name):
        res = self._post("/api/group/create", {"user_id": creator_id, "name": group_name})
        return res.get("group_id"), res.get("code")

    def join_group_by_code(self, user_id, join_code):
        res = self._post("/api/group/join", {"user_id": user_id, "code": join_code})
        return res.get("success", False)

    def get_user_groups(self, user_id):
        res = self._get(f"/api/groups/{user_id}")
        if isinstance(res, dict) and not res.get("success", True):
            return [] # 發生錯誤時回傳空列表，避免 UI 迭代報錯
        return res if isinstance(res, list) else []

    def get_group_members(self, group_id):
        res = self._get(f"/api/group/{group_id}/members")
        if isinstance(res, dict) and not res.get("success", True):
            return []
        return res if isinstance(res, list) else []

    # --- 交易相關轉發 ---
    def propose_transaction(self, transaction_id, payer_id, amount, participants, 
                          group_id, custom_splits=None, tx_type="EXPENSE", 
                          description="", location="", timestamp=None, category="OTHER"):
        data = {
            "transaction_id": transaction_id,
            "payer_id": payer_id,
            "amount": float(amount),
            "participants": participants,
            "group_id": group_id,
            "custom_splits": custom_splits,
            "tx_type": tx_type,
            "category": category,
            "description": description,
            "location": location,
            "timestamp": timestamp.isoformat() if timestamp else None
        }
        res = self._post("/api/transaction/propose", data)
        return res.get("success", False)

    def update_transaction(self, transaction_id, amount_float, participants, 
                          custom_splits=None, description="", location="", timestamp=None):
        data = {
            "transaction_id": transaction_id,
            "amount": float(amount_float),
            "participants": participants,
            "custom_splits": custom_splits,
            "description": description,
            "location": location,
            "timestamp": timestamp.isoformat() if timestamp else None
        }
        res = self._post("/api/transaction/update", data)
        return res.get("success", False)

    def confirm_transaction(self, user_id, transaction_id, status=None):
        res = self._post("/api/transaction/confirm", {"user_id": user_id, "transaction_id": transaction_id, "status": status})
        return res.get("success", False)

    def get_group_transactions(self, group_id):
        res = self._get(f"/api/group/{group_id}/transactions")
        if isinstance(res, dict) and not res.get("success", True):
            return []
        return res if isinstance(res, list) else []

    def get_group_balances(self, group_id):
        return self._get(f"/api/group/{group_id}/balances")

    def settle_debts(self, group_id, user_id, mode="ORIGINAL"):
        res = self._post("/api/group/settle", {"group_id": group_id, "user_id": user_id, "mode": mode})
        return res.get("plan", [])

    # --- 個人中心與歷史 ---
    def get_personal_debts(self, user_id):
        res = self._get(f"/api/user/{user_id}/debts")
        if isinstance(res, dict) and not res.get("success", True):
            return [], [] # 返回雙空列表，防止解構失敗
        return res.get("payables", []), res.get("receivables", [])

    def get_user_summary(self, user_id):
        res = self._get(f"/api/user/{user_id}/summary")
        if isinstance(res, dict) and not res.get("success", True):
            return {}
        return res if isinstance(res, dict) else {}

    def get_personal_history(self, user_id):
        return self._get(f"/api/user/{user_id}/history")

    def get_transaction_details(self, tx_id):
        return self._get(f"/api/transaction/{tx_id}/details")

    # --- 工具相關 ---
    def repay_transaction(self, group_id, tx_id, debtor_id, creditor_id, amount):
        data = {"group_id": group_id, "tx_id": tx_id, "debtor_id": debtor_id, "creditor_id": creditor_id, "amount": amount}
        res = self._post("/api/transaction/repay", data)
        return res.get("success", False)

    def request_settlement(self, debtor_id, creditor_id, amount, method, tx_ids):
        data = {"debtor_id": debtor_id, "creditor_id": creditor_id, "amount": amount, "method": method, "tx_ids": tx_ids}
        res = self._post("/api/transaction/request_settlement", data)
        return res.get("success", False)

    def get_notification_message(self, tx_id):
        res = self._get(f"/api/transaction/{tx_id}/notification")
        return res.get("message", "無法獲取通知訊息")



    def reject_transaction(self, user_id, tx_id):
        res = self._post("/api/transaction/reject", {"user_id": user_id, "transaction_id": tx_id})
        return res.get("success", False)

    def check_overdue_transactions(self):
        return self._get("/api/system/overdue")

    def settle_specific_debts(self, debtor_id, creditor_id, tx_ids):
        res = self._post("/api/transaction/settle_specific", {"debtor_id": debtor_id, "creditor_id": creditor_id, "tx_ids": tx_ids})
        return res.get("success", False)


    def generate_group_bill_summary(self, group_id):
        res = self._get(f"/api/group/{group_id}/summary")
        return res.get("summary", "無法生成摘要")

    def delete_group(self, group_id):
        try:
            res = requests.delete(f"{self.base_url}/api/group/{group_id}", timeout=5)
            return res.json().get("success", False)
        except: return False

    def delete_transaction(self, tx_id):
        try:
            res = requests.delete(f"{self.base_url}/api/transaction/{tx_id}", timeout=5)
            return res.json().get("success", False)
        except: return False
