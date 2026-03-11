import qrcode
import os
from .base import BaseService
from .models import TransactionStatus

class PersonalService(BaseService):
    """個人服務模組：負責好友管理與個人債務統計 (由 Person A 負責)"""
    
    def add_friend(self, user_id, friend_id):
        """建立好友關係 (雙向)"""
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
        
        path = f"data/qr_{user_id}.png"
        img.save(path)
        return os.path.abspath(path)

    def get_personal_debts(self, user_id):
        """獲取個人所有的欠款（應付）與應收項目"""
        payables = [] # 我欠別人的
        receivables = [] # 別人欠我的
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 應付
            cursor.execute("""
                SELECT tp.transaction_id, t.payer_id, tp.owed_amount, t.timestamp, tp.status, t.description, t.location
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE tp.user_id = ? AND t.payer_id != ? AND tp.status != ? AND t.type = 'EXPENSE'
            """, (user_id, user_id, TransactionStatus.SETTLED.name))
            payables = [{"tx_id": r[0], "creditor": r[1], "amount": r[2], "date": r[3], "status": r[4], "desc": r[5], "loc": r[6]} for r in cursor.fetchall()]
            
            # 應收
            cursor.execute("""
                SELECT tp.transaction_id, tp.user_id, tp.owed_amount, t.timestamp, tp.status, t.description, t.location
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE t.payer_id = ? AND tp.user_id != ? AND tp.status != ? AND t.type = 'EXPENSE'
            """, (user_id, user_id, TransactionStatus.SETTLED.name))
            receivables = [{"tx_id": r[0], "debtor": r[1], "amount": r[2], "date": r[3], "status": r[4], "desc": r[5], "loc": r[6]} for r in cursor.fetchall()]
            
        return payables, receivables

    def get_user_summary(self, user_id):
        """獲取使用者與所有人的債務關係簡要總結"""
        payables, receivables = self.get_personal_debts(user_id)
        summary = {} # {使用者ID: 餘額}
        
        for p in payables:
            creditor = p["creditor"]
            summary[creditor] = summary.get(creditor, 0) - p["amount"]
        
        for r in receivables:
            debtor = r["debtor"]
            summary[debtor] = summary.get(debtor, 0) + r["amount"]
            
        return summary
