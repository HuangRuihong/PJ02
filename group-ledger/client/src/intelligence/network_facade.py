import requests
import json
import time
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import os

from dotenv import load_dotenv

# 載入 .env 檔案 (精確定位 client/.env)
client_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(client_dir, ".env"))

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

    def _request(self, method, path, data=None, retries=2):
        """統一的請求處理核心，包含重試機制與精確錯誤解析"""
        for i in range(retries + 1):
            try:
                url = f"{self.base_url}{path}"
                if method == "POST":
                    res = requests.post(url, json=data, timeout=5)
                elif method == "DELETE":
                    res = requests.delete(url, timeout=5)
                else: # GET
                    res = requests.get(url, timeout=5)
                
                # 嘗試解析 JSON，無論狀態碼為何
                try:
                    res_json = res.json()
                except:
                    res_json = {}

                # 如果 HTTP 狀態碼代表錯誤，且 Response 中有詳細錯誤訊息，則優先使用
                if not (200 <= res.status_code < 300):
                    if isinstance(res_json, dict) and "detail" in res_json:
                        # FastAPI 的 HTTPException detail 可能是我們定義的 error_response
                        detail = res_json["detail"]
                        if isinstance(detail, dict) and not detail.get("success"):
                            return detail
                    return {"success": False, "error": f"伺服器錯誤 ({res.status_code})"}
                
                return res_json
            except Exception as e:
                if i == retries:
                    return {"success": False, "error": f"網路連線異常: {str(e)}"}
                time.sleep(0.5)

    def _post(self, path, data, retries=2):
        return self._request("POST", path, data, retries)

    def _get(self, path, retries=2):
        return self._request("GET", path, None, retries)

    def _delete(self, path, retries=2):
        return self._request("DELETE", path, None, retries)

    # --- 群組相關轉發 ---
    def create_group_with_code(self, creator_id, group_name):
        res = self._post("/api/group/create", {"user_id": creator_id, "name": group_name})
        data = res.get("data", {}) if res.get("success") else {}
        return data.get("group_id"), data.get("code")

    def join_group_by_code(self, user_id, join_code):
        res = self._post("/api/group/join", {"user_id": user_id, "code": join_code})
        return res.get("success", False)

    def get_user_groups(self, user_id):
        res = self._get(f"/api/groups/{user_id}")
        return res.get("data", []) if res.get("success") else []

    def get_group_members(self, group_id):
        res = self._get(f"/api/group/{group_id}/members")
        return res.get("data", []) if res.get("success") else []

    # --- 交易相關轉發 ---
    def propose_transaction(self, transaction_id, payer_id, amount, participants, 
                          group_id, custom_splits=None, tx_type="EXPENSE", 
                          description="", location="", timestamp=None, category="OTHER"):
        data = {
            "transaction_id": transaction_id, "payer_id": payer_id, "amount": float(amount),
            "participants": participants, "group_id": group_id, "custom_splits": custom_splits,
            "tx_type": tx_type, "category": category, "description": description,
            "location": location, "timestamp": timestamp.isoformat() if timestamp else None
        }
        res = self._post("/api/transaction/propose", data)
        return res.get("success", False)

    def update_transaction(self, transaction_id, amount_float, participants, 
                          custom_splits=None, description="", location="", timestamp=None):
        data = {
            "transaction_id": transaction_id, "amount": float(amount_float),
            "participants": participants, "custom_splits": custom_splits,
            "description": description, "location": location,
            "timestamp": timestamp.isoformat() if timestamp else None
        }
        res = self._post("/api/transaction/update", data)
        return res.get("success", False)

    def confirm_transaction(self, user_id, transaction_id, status=None):
        res = self._post("/api/transaction/confirm", {"user_id": user_id, "transaction_id": transaction_id, "status": status})
        return res.get("success", False)

    def get_group_transactions(self, group_id):
        res = self._get(f"/api/group/{group_id}/transactions")
        return res.get("data", []) if res.get("success") else []

    def get_group_balances(self, group_id):
        res = self._get(f"/api/group/{group_id}/balances")
        return res.get("data", {}) if res.get("success") else {}

    def settle_debts(self, group_id, user_id, mode="ORIGINAL"):
        res = self._post("/api/group/settle", {"group_id": group_id, "user_id": user_id, "mode": mode})
        return res.get("data", {}) if res.get("success") else {}

    # --- 個人中心與歷史 ---
    def get_personal_debts(self, user_id):
        res = self._get(f"/api/user/{user_id}/debts")
        if res.get("success"):
            data = res.get("data", {})
            return data.get("payables", []), data.get("receivables", [])
        return [], []

    def get_user_summary(self, user_id):
        res = self._get(f"/api/user/{user_id}/summary")
        return res.get("data", {}) if res.get("success") else {}

    def get_personal_history(self, user_id):
        res = self._get(f"/api/user/{user_id}/history")
        return res.get("data", []) if res.get("success") else []

    def get_transaction_details(self, tx_id):
        res = self._get(f"/api/transaction/{tx_id}/details")
        return res.get("data", {}) if res.get("success") else {}

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
        data = res.get("data", {}) if res.get("success") else {}
        return data.get("message", "無法獲取通知訊息")

    def reject_transaction(self, user_id, tx_id):
        res = self._post("/api/transaction/reject", {"user_id": user_id, "transaction_id": tx_id})
        return res.get("success", False)

    def check_overdue_transactions(self):
        res = self._get("/api/system/overdue")
        return res.get("data", []) if res.get("success") else []

    def settle_specific_debts(self, debtor_id, creditor_id, tx_ids):
        res = self._post("/api/transaction/settle_specific", {"debtor_id": debtor_id, "creditor_id": creditor_id, "tx_ids": tx_ids})
        return res.get("success", False)

    def generate_group_bill_summary(self, group_id):
        res = self._get(f"/api/group/{group_id}/summary")
        data = res.get("data", {}) if res.get("success") else {}
        return data.get("summary", "無法生成摘要")

    def delete_group(self, group_id):
        res = self._delete(f"/api/group/{group_id}")
        return res.get("success", False)

    def delete_transaction(self, tx_id):
        res = self._delete(f"/api/transaction/{tx_id}")
        return res.get("success", False)
