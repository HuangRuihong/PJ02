import qrcode
import os
from .base import BaseService
from .models import TransactionStatus

class PersonalService(BaseService):
    """個人服務模組：負責好友管理與個人債務統計 (由 Person A 負責)"""
    
    def add_friend(self, user_id, friend_id):
        """建立好友關係 (雙向)"""
        # 防止加自己為好友
        if str(user_id) == str(friend_id):
            return False
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
                cursor.execute("INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)", (friend_id, user_id))
                return True
            except Exception: return False

    def get_friends(self, user_id):
        """獲取好友清單"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT friend_id FROM friends WHERE user_id = ?", (user_id,))
            return [r[0] for r in cursor.fetchall()]

    def generate_qr_path(self, user_id):
        """產生 QR Code 圖片並傳回暫存路徑"""
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(user_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        path = os.path.join(data_dir, f"qr_{user_id}.png")
        img.save(path)
        return os.path.abspath(path)

    def get_personal_debts(self, user_id):
        """獲取個人所有的欠款（應付）與應收項目"""
        payables = [] # 我欠別人的
        receivables = [] # 別人欠我的
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 應付 (包含待確認與已確認，排除已結清或已退回項目)
            cursor.execute("""
                SELECT tp.transaction_id, t.payer_id, tp.owed_amount, t.timestamp, tp.status, t.description, t.location, t.type
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE tp.user_id = ? AND t.payer_id != ? 
                AND tp.status != ? AND t.status != 'REJECTED'
                AND t.type IN ('EXPENSE', 'REPAY_REQUEST')
            """, (user_id, user_id, TransactionStatus.SETTLED.name))
            payables = [{"tx_id": r[0], "creditor": r[1], "amount": r[2], "date": r[3], "status": r[4], "desc": r[5], "loc": r[6], "type": r[7]} for r in cursor.fetchall()]
            
            # 應收 (包含待確認與已確認，排除已退回)
            cursor.execute("""
                SELECT tp.transaction_id, tp.user_id, tp.owed_amount, t.timestamp, tp.status, t.description, t.location, t.type
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE t.payer_id = ? AND tp.user_id != ? 
                AND tp.status != ? AND t.status != 'REJECTED'
                AND t.type IN ('EXPENSE', 'REPAY_REQUEST')
            """, (user_id, user_id, TransactionStatus.SETTLED.name))
            receivables = [{"tx_id": r[0], "debtor": r[1], "amount": r[2], "date": r[3], "status": r[4], "desc": r[5], "loc": r[6], "type": r[7]} for r in cursor.fetchall()]
            
        return payables, receivables

    def request_settlement(self, debtor_id, creditor_id, amount, method, tx_ids):
        """發起一個還款確認請求 (對方會在待辦事項收到)"""
        from datetime import datetime
        import random
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                s_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(100, 999)}"
                loc = ",".join(tx_ids) # 暫存要結清的 tx_ids
                desc = f"[結清申請] 透過 {method} 償還"
                
                # 建立主交易 (債務人發起)
                cursor.execute("""
                    INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, location, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (s_id, "PERSONAL", debtor_id, amount, TransactionStatus.PENDING.name, 'REPAY_REQUEST', desc, loc, datetime.now()))
                
                # 參與者是債權人 (待確認)
                cursor.execute("""
                    INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status)
                    VALUES (?, ?, ?, ?)
                """, (s_id, creditor_id, amount, TransactionStatus.PENDING.name))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Request settlement Error: {e}")
                return False

    def reject_transaction(self, user_id, transaction_id):
        """拒絕一筆尚未確認的帳款或結清申請"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE transaction_participants SET status = 'REJECTED' WHERE transaction_id = ? AND user_id = ?", (transaction_id, user_id))
                conn.commit()
                return True
            except:
                return False

    def get_personal_history(self, user_id):
        """獲取個人的所有支出歷史 (含各群組代墊)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 取得該用戶作為 Payer 或是參與者的所有交易
            cursor.execute("""
                SELECT t.transaction_id, t.group_id, t.amount, t.description, t.timestamp, t.status, t.payer_id, 
                       CASE WHEN t.group_id = 'PERSONAL' THEN '👤 個人私帳' ELSE COALESCE(g.name, t.group_id) END as group_name,
                       tp.owed_amount
                FROM transactions t
                JOIN transaction_participants tp ON t.transaction_id = tp.transaction_id
                LEFT JOIN groups g ON t.group_id = g.group_id
                WHERE tp.user_id = ? AND t.type IN ('EXPENSE', 'SETTLEMENT')
                ORDER BY t.timestamp DESC
            """, (user_id,))
            return [{"id": r[0], "group_id": r[1], "amount": r[2], "description": r[3], "timestamp": r[4], 
                     "status": r[5], "payer_id": r[6], "group_name": r[7], "my_share": r[8]} for r in cursor.fetchall()]

    def get_user_summary(self, user_id):
        """獲取使用者與所有人的債務關係簡要總結 (落實一票否決：僅統計全局狀態為 CONFIRMED 的交易)"""
        # 這裡需要傳入 t.status 的資訊，或者直接在這裡寫 SQL 會更精準高效
        summary = {} # {使用者ID: 餘額}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 統計我應付給別人的 (排除 PENDING/REJECTED/SETTLED)
            cursor.execute("""
                SELECT t.payer_id, SUM(tp.owed_amount)
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE tp.user_id = ? AND t.payer_id != ?
                AND tp.status = 'CONFIRMED' AND t.status = 'CONFIRMED'
                AND t.type IN ('EXPENSE', 'REPAY_REQUEST')
                GROUP BY t.payer_id
            """, (user_id, user_id))
            for creditor, amount in cursor.fetchall():
                summary[creditor] = summary.get(creditor, 0) - amount
            
            # 統計別人應付給我的 (排除 PENDING/REJECTED/SETTLED)
            cursor.execute("""
                SELECT tp.user_id, SUM(tp.owed_amount)
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE t.payer_id = ? AND tp.user_id != ?
                AND tp.status = 'CONFIRMED' AND t.status = 'CONFIRMED'
                AND t.type IN ('EXPENSE', 'REPAY_REQUEST')
                GROUP BY tp.user_id
            """, (user_id, user_id))
            for debtor, amount in cursor.fetchall():
                summary[debtor] = summary.get(debtor, 0) + amount
                
        return summary
