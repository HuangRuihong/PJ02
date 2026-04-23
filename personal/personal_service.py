from shared.base_service import BaseService
from shared.models import TransactionStatus

class PersonalService(BaseService):
    """
    個人服務模組 (Person A)：負責好友管理與個人中心數據彙整。
    
    優化說明：已移除廢棄的 QR Code 生成邏輯，改為輕量化架構。
    """
    def add_friend(self, user_id, friend_id):
        """建立好友關係 (雙向)"""
        if str(user_id) == str(friend_id): return False
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
                cursor.execute("INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)", (friend_id, user_id))
                conn.commit()
                return True
            except Exception: return False

    def get_friends(self, user_id):
        """獲取好友清單"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT friend_id FROM friends WHERE user_id = ?", (user_id,))
            return [r[0] for r in cursor.fetchall()]

    def get_personal_debts(self, user_id):
        """獲取個人所有的欠款（應付）與應收項目 (包含群組帳與私帳)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 應付：我是參與者且對方是付款人
            cursor.execute("""
                SELECT tp.transaction_id, t.payer_id, tp.owed_amount, t.timestamp, tp.status, t.description, t.location, t.type
                FROM transaction_participants tp JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE tp.user_id = ? AND t.payer_id != ? AND tp.status != ? AND t.status != 'REJECTED'
                AND t.type IN ('EXPENSE', 'REPAY_REQUEST', 'SETTLEMENT')
            """, (user_id, user_id, TransactionStatus.SETTLED.name))
            payables = [{"tx_id":r[0],"creditor":r[1],"amount":r[2],"date":r[3],"status":r[4],"desc":r[5],"loc":r[6],"type":r[7]} for r in cursor.fetchall()]
            
            # 應收：我是付款人且對方是參與者
            cursor.execute("""
                SELECT tp.transaction_id, tp.user_id, tp.owed_amount, t.timestamp, tp.status, t.description, t.location, t.type
                FROM transaction_participants tp JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE t.payer_id = ? AND tp.user_id != ? AND tp.status != ? AND t.status != 'REJECTED'
                AND t.type IN ('EXPENSE', 'REPAY_REQUEST', 'SETTLEMENT')
            """, (user_id, user_id, TransactionStatus.SETTLED.name))
            receivables = [{"tx_id":r[0],"debtor":r[1],"amount":r[2],"date":r[3],"status":r[4],"desc":r[5],"loc":r[6],"type":r[7]} for r in cursor.fetchall()]
        return payables, receivables

    def request_settlement(self, debtor_id, creditor_id, amount, method, tx_ids):
        """發起還款確認請求"""
        from datetime import datetime
        import random
        try:
            with self._get_connection() as conn:
                cursor, s_id = conn.cursor(), f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(100, 999)}"
                cursor.execute("INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, location, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (s_id, "PERSONAL", debtor_id, amount, TransactionStatus.PENDING.name, 'REPAY_REQUEST', f"[結清申請] 透過 {method} 償還", ",".join(tx_ids), datetime.now()))
                cursor.execute("INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status) VALUES (?, ?, ?, ?)",
                             (s_id, creditor_id, amount, TransactionStatus.PENDING.name))
                conn.commit()
                return True
        except: return False

    def get_personal_history(self, user_id):
        """獲取個人的所有帳務歷史紀錄"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.transaction_id, t.group_id, t.amount, t.description, t.timestamp, t.status, t.payer_id, 
                       CASE WHEN t.group_id = 'PERSONAL' THEN '[個人私帳]' ELSE COALESCE(g.name, t.group_id) END, tp.owed_amount
                FROM transactions t JOIN transaction_participants tp ON t.transaction_id = tp.transaction_id
                LEFT JOIN groups g ON t.group_id = g.group_id
                WHERE tp.user_id = ? AND t.type IN ('EXPENSE', 'SETTLEMENT', 'REPAY_REQUEST') ORDER BY t.timestamp DESC
            """, (user_id,))
            return [{"id":r[0],"group_id":r[1],"amount":r[2],"description":r[3],"timestamp":r[4],"status":r[5],"payer_id":r[6],"group_name":r[7],"my_share":r[8]} for r in cursor.fetchall()]

    def get_user_summary(self, user_id):
        """獲取使用者與所有人的債務關係總結 (單一 SQL 高效優化版)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    CASE WHEN t.payer_id = ? THEN tp.user_id ELSE t.payer_id END as other_user,
                    SUM(CASE WHEN t.payer_id = ? THEN tp.owed_amount ELSE -tp.owed_amount END) as balance
                FROM transactions t JOIN transaction_participants tp ON t.transaction_id = tp.transaction_id
                WHERE (t.payer_id = ? OR tp.user_id = ?) AND t.payer_id != tp.user_id
                  AND t.status = 'CONFIRMED' AND tp.status = 'CONFIRMED' AND t.type IN ('EXPENSE', 'REPAY_REQUEST')
                GROUP BY other_user
            """, (user_id, user_id, user_id, user_id))
            return {r[0]: r[1] for r in cursor.fetchall()}
