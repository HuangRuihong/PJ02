import requests
import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import os

class NetworkDebtSystem:
    """
    網路代理類別：將所有原有的數據庫呼叫改寫為 REST API 網路請求。
    它完美替代了本地的 DebtSystem，讓 GUI 無需大規模重規即能聯網。
    """
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.current_user = None

    def _post(self, path, data):
        try:
            res = requests.post(f"{self.base_url}{path}", json=data, timeout=5)
            return res.json()
        except Exception as e:
            print(f"Network Error (POST {path}): {e}")
            return {"success": False, "error": str(e)}

    def _get(self, path):
        try:
            res = requests.get(f"{self.base_url}{path}", timeout=5)
            return res.json()
        except Exception as e:
            print(f"Network Error (GET {path}): {e}")
            return [] if "/groups" in path or "/members" in path else {}

    # --- 群組相關轉發 ---
    def create_group_with_code(self, creator_id, group_name):
        res = self._post("/api/group/create", {"creator_id": creator_id, "group_name": group_name})
        return res.get("group_id"), res.get("join_code")

    def join_group_by_code(self, user_id, join_code):
        res = self._post("/api/group/join", {"user_id": user_id, "join_code": join_code})
        return res.get("success", False)

    def get_user_groups(self, user_id):
        return self._get(f"/api/user/{user_id}/groups")

    def get_group_members(self, group_id):
        return self._get(f"/api/group/{group_id}/members")

    # --- 交易相關轉發 ---
    def propose_transaction(self, transaction_id, payer_id, amount, participants, 
                          group_id, custom_splits=None, tx_type="EXPENSE", 
                          description="", location="", timestamp=None):
        data = {
            "transaction_id": transaction_id,
            "payer_id": payer_id,
            "amount": float(amount),
            "participants": participants,
            "group_id": group_id,
            "custom_splits": custom_splits,
            "tx_type": tx_type,
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
        return self._get(f"/api/group/{group_id}/transactions")

    def get_group_balances(self, group_id):
        return self._get(f"/api/group/{group_id}/balances")

    def settle_debts(self, group_id, user_id, mode="ORIGINAL"):
        res = self._post("/api/group/settle", {"group_id": group_id, "user_id": user_id, "mode": mode})
        return res.get("plan", [])

    # --- 個人中心與歷史 ---
    def get_personal_debts(self, user_id):
        res = self._get(f"/api/user/{user_id}/debts")
        return res.get("payables", []), res.get("receivables", [])

    def get_user_summary(self, user_id):
        return self._get(f"/api/user/{user_id}/summary")

    def get_personal_history(self, user_id):
        return self._get(f"/api/user/{user_id}/history")

    def get_transaction_details(self, tx_id):
        return self._get(f"/api/transaction/{tx_id}/details")

    # --- 工具相關 ---
    def repay_transaction(self, group_id, tx_id, debtor_id, creditor_id, amount):
        data = {"group_id": group_id, "tx_id": tx_id, "debtor_id": debtor_id, "creditor_id": creditor_id, "amount": amount}
        res = self._post("/api/transaction/repay", data)
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

    def get_group_budget_status(self, group_id):
        return self._get(f"/api/group/{group_id}/budget")

    def set_group_budget(self, group_id, amount):
        res = self._post(f"/api/group/{group_id}/budget", {"group_id": group_id, "amount": amount})
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
