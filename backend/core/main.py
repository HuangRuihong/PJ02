from .models import TransactionStatus, TransactionType
from .personal_service import PersonalService
from .group_service import GroupService

class DebtSystem(PersonalService, GroupService):
    """
    債務系統外觀類別 (Facade)：整合個人務與群組服務。
    
    此類別繼承自 PersonalService (Person A) 與 GroupService (Person B)，
    為 UI 層提供統一的 API 接口。
    """
    def __init__(self, db_path=None):
        # 呼叫父類別 (BaseService) 的初始化方法
        super().__init__(db_path=db_path)

    # 為了保持與舊版代碼的絕對相容性，保留部分特定方法的別名或封裝
    def create_group(self, group_id, group_name, creator_id):
        """建立一個新群組 (手動指定 ID)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO groups (group_id, name) VALUES (?, ?)", (group_id, group_name))
                cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, creator_id))
                return True
        except Exception: return False

    def add_member_to_group(self, group_id, user_id):
        """將特定成員加入群組"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, user_id))
                return True
        except Exception: return False
        
    def settle_specific_debts(self, debtor_id, creditor_id, tx_ids):
        """批量結算特定的欠款項目"""
        from datetime import datetime
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                now = datetime.now()
                total_settled = 0
                for tid in tx_ids:
                    cursor.execute("SELECT owed_amount FROM transaction_participants WHERE transaction_id = ? AND user_id = ?", (tid, debtor_id))
                    row = cursor.fetchone()
                    if row:
                        total_settled += row[0]
                        cursor.execute("""
                            UPDATE transaction_participants 
                            SET status = ?, settled_at = ? 
                            WHERE transaction_id = ? AND user_id = ?
                        """, (TransactionStatus.SETTLED.name, now, tid, debtor_id))
                
                s_id = f"st_{datetime.now().strftime('%Y%m%d%H%M%S')}_{debtor_id}"
                cursor.execute("""
                    INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (s_id, "g1", debtor_id, total_settled, TransactionStatus.SETTLED.name, TransactionType.SETTLEMENT.name, now))
                
                cursor.execute("""
                    INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status, settled_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (s_id, creditor_id, -total_settled, TransactionStatus.SETTLED.name, now))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Settlement Error: {e}")
                return False

    def calculate_balances(self, group_id):
        """計算群組內所有成員的累積餘額"""
        balances = {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
            for row in cursor.fetchall(): balances[row[0]] = 0
                
            cursor.execute("""
                SELECT tp.user_id, tp.owed_amount, t.payer_id, t.type
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE t.group_id = ? AND tp.status IN (?, ?)
            """, (group_id, TransactionStatus.CONFIRMED.name, TransactionStatus.SETTLED.name))
            
            for debtor_id, amount, payer_id, tx_type in cursor.fetchall():
                if debtor_id != payer_id:
                    balances[debtor_id] -= amount
                    balances[payer_id] += amount
        return balances

    def get_settlement_history(self, user_id):
        """獲取與個人相關的還款紀錄歷史"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.transaction_id, t.payer_id, t.amount, t.timestamp, tp.user_id
                FROM transactions t
                JOIN transaction_participants tp ON t.transaction_id = tp.transaction_id
                WHERE (t.payer_id = ? OR tp.user_id = ?) AND t.type = 'SETTLEMENT'
                ORDER BY t.timestamp DESC
            """, (user_id, user_id))
            return [{"id": r[0], "payer": r[1], "amount": r[2], "date": r[3], "receiver": r[4]} for r in cursor.fetchall()]

    def get_personal_history(self, user_id):
        """獲取個人的所有支出歷史 (Facade)"""
        return super().get_personal_history(user_id)

    def check_overdue_transactions(self):
        """
        自動化逾期掃描：根據金額動態建議期限。
        - ≤ 500 元: 7 天
        - 501 ~ 2000 元: 14 天
        - > 2000 元: 30 天
        """
        from datetime import datetime
        overdue_list = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tp.transaction_id, tp.user_id, t.timestamp, tp.owed_amount, t.description
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE tp.status = ? AND t.type = 'EXPENSE'
            """, (TransactionStatus.PENDING.name,))
            
            for tx_id, user_id, ts_str, amount, desc in cursor.fetchall():
                ts = datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else ts_str
                diff_days = (datetime.now() - ts).days
                
                # 動態期限邏輯
                if amount <= 500: limit = 7
                elif amount <= 2000: limit = 14
                else: limit = 30
                
                if diff_days >= limit:
                    overdue_list.append({
                        "id": tx_id, 
                        "user": user_id, 
                        "amount": amount, 
                        "days": diff_days, 
                        "limit": limit,
                        "desc": desc
                    })
        return overdue_list
