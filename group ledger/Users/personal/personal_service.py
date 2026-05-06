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
            # 【應付款項】(Payables)：我是參與者 (需要付錢)，而對方是代墊人 (需要收錢)
            cursor.execute("""
                SELECT 
                    tp.transaction_id, t.payer_id, tp.owed_amount, t.timestamp, 
                    tp.status, t.description, t.location, t.type, t.category
                FROM transaction_participants tp 
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE tp.user_id = ?        -- 條件1：我是參與者
                  AND t.payer_id != ?       -- 條件2：但我不是這筆帳單的代墊人
                  AND tp.status != ?        -- 條件3：這筆帳務尚未結清 (非 SETTLED)
                  AND t.status != 'REJECTED'-- 條件4：整筆帳單未被作廢
                  AND t.type IN ('EXPENSE', 'REPAY_REQUEST', 'SETTLEMENT')
            """, (user_id, user_id, TransactionStatus.SETTLED.name))
            payables = [{"tx_id":r[0],"creditor":r[1],"amount":r[2],"date":r[3],"status":r[4],"desc":r[5],"loc":r[6],"type":r[7],"category":r[8]} for r in cursor.fetchall()]
            
            # 【應收款項】(Receivables)：我是代墊人 (需要收錢)，而對方是參與者 (需要付錢)
            cursor.execute("""
                SELECT 
                    tp.transaction_id, tp.user_id, tp.owed_amount, t.timestamp, 
                    tp.status, t.description, t.location, t.type, t.category
                FROM transaction_participants tp 
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE t.payer_id = ?        -- 條件1：我是代墊人
                  AND tp.user_id != ?       -- 條件2：對方不是我本人
                  AND tp.status != ?        -- 條件3：對方尚未結清 (非 SETTLED)
                  AND t.status != 'REJECTED'-- 條件4：整筆帳單未被作廢
                  AND t.type IN ('EXPENSE', 'REPAY_REQUEST', 'SETTLEMENT')
            """, (user_id, user_id, TransactionStatus.SETTLED.name))
            receivables = [{"tx_id":r[0],"debtor":r[1],"amount":r[2],"date":r[3],"status":r[4],"desc":r[5],"loc":r[6],"type":r[7],"category":r[8]} for r in cursor.fetchall()]
        return payables, receivables

    def request_settlement(self, debtor_id, creditor_id, amount, method, tx_ids):
        """發起私下還款請求：透過建立一個虛擬的個人帳單 (PERSONAL) 來記錄還款"""
        import uuid
        from datetime import datetime
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                s_id = f"req_{uuid.uuid4().hex[:8]}"
                
                # 1. 寫入總帳：將還款行為視為一筆特殊的 'REPAY_REQUEST' 交易
                cursor.execute("""
                    INSERT INTO transactions 
                    (transaction_id, group_id, payer_id, amount, status, type, description, location, timestamp, category) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (s_id, "PERSONAL", debtor_id, amount, TransactionStatus.PENDING.name, 
                      'REPAY_REQUEST', f"[結清申請] 透過 {method} 償還", ",".join(tx_ids), datetime.now(), 'OTHER'))
                
                # 2. 寫入參與者：指定收款人 (creditor_id) 為這筆還款單的目標對象
                cursor.execute("""
                    INSERT INTO transaction_participants 
                    (transaction_id, user_id, owed_amount, status) 
                    VALUES (?, ?, ?, ?)
                """, (s_id, creditor_id, amount, TransactionStatus.PENDING.name))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"發起還款請求失敗: {e}")
            return False

    def get_personal_history(self, user_id):
        """獲取個人的所有帳務歷史紀錄 (以時間倒序排列)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.transaction_id, t.group_id, t.amount, t.description, 
                    t.timestamp, t.status, t.payer_id, 
                    -- 判斷帳單來源：如果是私下轉帳顯示 '[個人私帳]'，否則顯示群組名稱
                    CASE WHEN t.group_id = 'PERSONAL' THEN '[個人私帳]' ELSE COALESCE(g.name, t.group_id) END as group_name, 
                    tp.owed_amount, t.category
                FROM transactions t 
                JOIN transaction_participants tp ON t.transaction_id = tp.transaction_id
                LEFT JOIN groups g ON t.group_id = g.group_id
                WHERE tp.user_id = ? 
                  AND t.type IN ('EXPENSE', 'SETTLEMENT', 'REPAY_REQUEST') 
                ORDER BY t.timestamp DESC -- 依時間由新到舊排序
            """, (user_id,))
            return [{"id":r[0],"group_id":r[1],"amount":r[2],"description":r[3],"timestamp":r[4],"status":r[5],"payer_id":r[6],"group_name":r[7],"my_share":r[8],"category":r[9]} for r in cursor.fetchall()]

    def get_user_summary(self, user_id):
        """
        獲取使用者與所有人的淨額債務總結 (高效優化版)
        - 若餘額為正 (+)：對方欠我錢
        - 若餘額為負 (-)：我欠對方錢
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    -- 判斷對方是誰：如果我是付款人，對方就是參與者；反之亦然
                    CASE WHEN t.payer_id = ? THEN tp.user_id ELSE t.payer_id END as other_user,
                    -- 結算淨額：如果我是付款人，該筆金額算我的應收(+)；反之為我的應付(-)
                    SUM(CASE WHEN t.payer_id = ? THEN tp.owed_amount ELSE -tp.owed_amount END) as balance
                FROM transactions t 
                JOIN transaction_participants tp ON t.transaction_id = tp.transaction_id
                WHERE (t.payer_id = ? OR tp.user_id = ?) -- 條件1：這筆帳必須跟我有關
                  AND t.payer_id != tp.user_id           -- 條件2：排除自己付給自己的項目
                  AND t.status = 'CONFIRMED'             -- 條件3：主帳單已確認
                  AND tp.status = 'CONFIRMED'            -- 條件4：參與者也已確認
                  AND t.type IN ('EXPENSE', 'REPAY_REQUEST')
                GROUP BY other_user
            """, (user_id, user_id, user_id, user_id))
            return {r[0]: r[1] for r in cursor.fetchall()}

    def get_spending_by_category(self, user_id):
        """統計各分類的支出總額 (僅統計有效且非拒絕狀態的支出)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.category,             -- 支出分類
                    SUM(tp.owed_amount)     -- 加總該使用者在此分類下的所有應付金額
                FROM transactions t
                JOIN transaction_participants tp ON t.transaction_id = tp.transaction_id
                WHERE tp.user_id = ?        -- 條件1：該使用者有參與
                  AND t.type = 'EXPENSE'    -- 條件2：必須是消費支出 (排除還款)
                  AND t.status != 'REJECTED'-- 條件3：帳單未被作廢
                GROUP BY t.category
            """, (user_id,))
            return {r[0]: r[1] for r in cursor.fetchall()}
