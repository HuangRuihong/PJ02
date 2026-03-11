import random
import string
import sqlite3
from datetime import datetime
from .base import BaseService
from .models import TransactionStatus, TransactionType

class GroupService(BaseService):
    """群組服務模組：負責群組管理、成員維護與交易分帳 (由 Person B 負責)"""

    def create_group_with_code(self, creator_id, group_name):
        """建立群組並產生 4 位英數邀群碼"""
        join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        group_id = f"g_{datetime.now().strftime('%m%d%H%M%S')}"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                while cursor.execute("SELECT 1 FROM groups WHERE join_code = ?", (join_code,)).fetchone():
                    join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                
                cursor.execute("INSERT INTO groups (group_id, name, join_code) VALUES (?, ?, ?)", (group_id, group_name, join_code))
                cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, creator_id))
                return group_id, join_code
        except Exception: return None, None

    def join_group_by_code(self, user_id, join_code):
        """透過 4 位代碼加入群組"""
        join_code = join_code.upper()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT group_id FROM groups WHERE join_code = ?", (join_code,))
            row = cursor.fetchone()
            if not row: return False
            
            group_id = row[0]
            try:
                cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, user_id))
                conn.commit()
                return True
            except sqlite3.IntegrityError: return True
            except Exception: return False

    def get_user_groups(self, user_id):
        """獲取使用者參加的所有群組"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.group_id, g.name, g.join_code 
                FROM groups g
                JOIN group_members gm ON g.group_id = gm.group_id
                WHERE gm.user_id = ?
            """, (user_id,))
            return [{"id": r[0], "name": r[1], "code": r[2]} for r in cursor.fetchall()]

    def get_group_members(self, group_id):
        """獲取指定群組的所有成員 ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
            return [row[0] for row in cursor.fetchall()]

    def propose_transaction(self, transaction_id, payer_id, amount_float, participants, group_id, custom_splits=None, tx_type=TransactionType.EXPENSE.name, description="", location=""):
        """發起一筆新交易並計算分帳"""
        amount_twd = int(round(amount_float))
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                splits = {}
                if custom_splits:
                    for uid, amt in custom_splits.items(): splits[uid] = int(round(amt))
                else:
                    count = len(participants)
                    if count > 0:
                        base = amount_twd // count
                        rem = amount_twd % count
                        for i, uid in enumerate(participants):
                            splits[uid] = base + (1 if i < rem else 0)

                cursor.execute("""
                    INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, location, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (transaction_id, group_id, payer_id, amount_twd, TransactionStatus.PENDING.name, tx_type, description, location, datetime.now()))
                
                for uid, owed in splits.items():
                    status = TransactionStatus.CONFIRMED.name if uid == payer_id else TransactionStatus.PENDING.name
                    cursor.execute("""
                        INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status)
                        VALUES (?, ?, ?, ?)
                    """, (transaction_id, uid, owed, status))
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False

    def confirm_transaction(self, user_id, transaction_id):
        """參與者確認交易項目"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transaction_participants SET status = ? 
                WHERE transaction_id = ? AND user_id = ? AND status = ?
            """, (TransactionStatus.CONFIRMED.name, transaction_id, user_id, TransactionStatus.PENDING.name))
            
            cursor.execute("SELECT COUNT(*) FROM transaction_participants WHERE transaction_id = ? AND status = ?", (transaction_id, TransactionStatus.PENDING.name))
            if cursor.fetchone()[0] == 0:
                cursor.execute("UPDATE transactions SET status = ? WHERE transaction_id = ?", (TransactionStatus.CONFIRMED.name, transaction_id))
            conn.commit()
            return True

    def get_group_transactions(self, group_id):
        """獲取群組的所有交易紀錄"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT transaction_id, payer_id, amount, status, type, description, location, timestamp
                FROM transactions
                WHERE group_id = ?
                ORDER BY timestamp DESC
            """, (group_id,))
            txs = []
            for r in cursor.fetchall():
                tx = {"id": r[0], "payer": r[1], "amount": r[2], "status": r[3], "type": r[4], "desc": r[5], "loc": r[6], "time": r[7]}
                cursor.execute("SELECT user_id FROM transaction_participants WHERE transaction_id = ? AND status = ?", (r[0], TransactionStatus.PENDING.name))
                tx["pending_confirmations"] = [p[0] for p in cursor.fetchall()]
                txs.append(tx)
            return txs
