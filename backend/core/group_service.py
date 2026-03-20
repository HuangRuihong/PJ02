import random
import string
import sqlite3
from datetime import datetime
from .base import BaseService
from .models import TransactionStatus, TransactionType

class GroupService(BaseService):
    """群組服務模組：負責群組管理、成員維護與交易分帳 (由 Person B 負責)"""

    def create_group_with_code(self, creator_id, group_name):
        """建立群組並產生 6 位英數邀群碼"""
        join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        group_id = f"g_{datetime.now().strftime('%m%d%H%M%S')}"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                while cursor.execute("SELECT 1 FROM groups WHERE join_code = ?", (join_code,)).fetchone():
                    join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                
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

    def set_group_budget(self, group_id, amount):
        """設定群組的總預算"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE groups SET budget = ? WHERE group_id = ?", (amount, group_id))
                conn.commit()
                return True
            except Exception: return False

    def get_group_budget_status(self, group_id):
        """獲取群組預算剩餘狀況 (預算 - 已支出)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. 取得總預算
            cursor.execute("SELECT budget FROM groups WHERE group_id = ?", (group_id,))
            row = cursor.fetchone()
            budget = row[0] if row else 0
            
            # 2. 取得該群組累積支出 (僅統計 EXPENSE 類型)
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE group_id = ? AND type = 'EXPENSE'", (group_id,))
            spent = cursor.fetchone()[0] or 0
            
            return {
                "budget": budget,
                "spent": spent,
                "remaining": budget - spent
            }

    def propose_transaction(self, transaction_id, payer_id, amount_float, participants, group_id, custom_splits=None, tx_type=TransactionType.EXPENSE.name, description="", location="", timestamp=None):
        """發起一筆新交易並計算分帳 (支援自定義時間)"""
        actual_ts = timestamp if timestamp else datetime.now()
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
                """, (transaction_id, group_id, payer_id, amount_twd, TransactionStatus.PENDING.name, tx_type, description, location, actual_ts))
                
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

    def confirm_transaction(self, user_id, transaction_id, status=None):
        """參與者確認交易項目 (預設為 CONFIRMED，若為還款可指定為 SETTLED)"""
        target_status = status if status else TransactionStatus.CONFIRMED.name
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transaction_participants SET status = ?, settled_at = ? 
                WHERE transaction_id = ? AND user_id = ? AND status != ?
            """, (target_status, datetime.now() if target_status == TransactionStatus.SETTLED.name else None, 
                  transaction_id, user_id, TransactionStatus.SETTLED.name))
            
            cursor.execute("SELECT COUNT(*) FROM transaction_participants WHERE transaction_id = ? AND status NOT IN (?, ?)", (transaction_id, TransactionStatus.CONFIRMED.name, TransactionStatus.SETTLED.name))
            if cursor.fetchone()[0] == 0:
                # 若所有人都確認/結清了，將主表狀態同步 (優先設為 SETTLED 如果有人選了這個，或者維持 CONFIRMED)
                cursor.execute("UPDATE transactions SET status = ? WHERE transaction_id = ?", (target_status, transaction_id))
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

    def get_group_balances(self, group_id):
        """計算群組內各成員的淨餘額 (應收 - 應付)"""
        balances = {}  # {user_id: net_amount}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 取得所有已確認且未結算的交易參與紀錄
            cursor.execute("""
                SELECT tp.user_id, tp.owed_amount, t.payer_id
                FROM transaction_participants tp
                JOIN transactions t ON tp.transaction_id = t.transaction_id
                WHERE t.group_id = ? AND t.status = ? AND tp.status = ?
            """, (group_id, TransactionStatus.CONFIRMED.name, TransactionStatus.CONFIRMED.name))
            
            rows = cursor.fetchall()
            for user_id, owed_amt, payer_id in rows:
                balances[user_id] = balances.get(user_id, 0) - owed_amt
                balances[payer_id] = balances.get(payer_id, 0) + owed_amt
            
            return {uid: amt for uid, amt in balances.items() if amt != 0}

    def settle_debts(self, group_id, execution_user_id, mode="ORIGINAL"):
        """
        執行結算：
        - ORIGINAL (預設): 保留原始債權關係，計算每位成員之間的淨額。
        - SIMPLIFIED: 債務抵銷模式，利用演算法極小化轉帳次數。
        """
        settlement_plan = []
        
        if mode == "SIMPLIFIED":
            balances = self.get_group_balances(group_id)
            if not balances: return []
            
            # 債務簡化演算法 (應付者給應收者路徑最小化)
            debtors = sorted([(u, amt) for u, amt in balances.items() if amt < 0], key=lambda x: x[1])
            creditors = sorted([(u, amt) for u, amt in balances.items() if amt > 0], key=lambda x: x[1], reverse=True)
            
            d_idx, c_idx = 0, 0
            while d_idx < len(debtors) and c_idx < len(creditors):
                d_id, d_amt = debtors[d_idx]
                c_id, c_amt = creditors[c_idx]
                pay_amt = min(abs(d_amt), c_amt)
                settlement_plan.append({"from": d_id, "to": c_id, "amount": pay_amt})
                debtors[d_idx] = (d_id, d_amt + pay_amt)
                creditors[c_idx] = (c_id, c_amt - pay_amt)
                if debtors[d_idx][1] == 0: d_idx += 1
                if creditors[c_idx][1] == 0: c_idx += 1
        else:
            # ORIGINAL 模式：統計每一對人之間的債權關係
            pair_debts = {} # {(debtor, creditor): amount}
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT tp.user_id, tp.owed_amount, t.payer_id
                    FROM transaction_participants tp
                    JOIN transactions t ON tp.transaction_id = t.transaction_id
                    WHERE t.group_id = ? AND t.status = ? AND tp.status = ?
                """, (group_id, TransactionStatus.CONFIRMED.name, TransactionStatus.CONFIRMED.name))
                for debtor, amount, creditor in cursor.fetchall():
                    if debtor == creditor: continue
                    pair = tuple(sorted((debtor, creditor)))
                    # 決定方向後加減
                    if debtor < creditor:
                        pair_debts[pair] = pair_debts.get(pair, 0) + amount
                    else:
                        pair_debts[pair] = pair_debts.get(pair, 0) - amount
                
                for (u1, u2), net in pair_debts.items():
                    if net > 0: settlement_plan.append({"from": u1, "to": u2, "amount": net})
                    elif net < 0: settlement_plan.append({"from": u2, "to": u1, "amount": abs(net)})

        # 標記更新狀態至資料庫
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT DISTINCT t.transaction_id FROM transactions t
                    JOIN transaction_participants tp ON t.transaction_id = tp.transaction_id
                    WHERE t.group_id = ? AND t.status = ? AND tp.status = ?
                """, (group_id, TransactionStatus.CONFIRMED.name, TransactionStatus.CONFIRMED.name))
                tids = [r[0] for r in cursor.fetchall()]
                
                for tid in tids:
                    cursor.execute("UPDATE transactions SET status = ? WHERE transaction_id = ?", (TransactionStatus.SETTLED.name, tid))
                    cursor.execute("UPDATE transaction_participants SET status = ?, settled_at = ? WHERE transaction_id = ?", 
                                (TransactionStatus.SETTLED.name, datetime.now(), tid))
                
                for item in settlement_plan:
                    s_id = f"repay_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(100, 999)}"
                    cursor.execute("""
                        INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (s_id, group_id, item['from'], item['amount'], TransactionStatus.SETTLED.name, 
                          TransactionType.SETTLEMENT.name, f"系統自動結算({mode})：還款給 {item['to']}", datetime.now()))
                    
                    cursor.execute("INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status, settled_at) VALUES (?, ?, ?, ?, ?)",
                                (s_id, item['to'], item['amount'], TransactionStatus.SETTLED.name, datetime.now()))
                    cursor.execute("INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status, settled_at) VALUES (?, ?, ?, ?, ?)",
                                (s_id, item['from'], 0, TransactionStatus.SETTLED.name, datetime.now()))
                conn.commit()
                return settlement_plan
            except Exception as e:
                print(f"Settlement Error: {e}")
                conn.rollback()
                return []

    def delete_group(self, group_id):
        """徹底刪除群組及其關聯的所有數據 (交易、參與者、成員)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                # 1. 刪除交易參與者紀錄 (需要先找到該群組的所有交易 ID)
                cursor.execute("""
                    DELETE FROM transaction_participants 
                    WHERE transaction_id IN (SELECT transaction_id FROM transactions WHERE group_id = ?)
                """, (group_id,))
                
                # 2. 刪除交易主表紀錄
                cursor.execute("DELETE FROM transactions WHERE group_id = ?", (group_id,))
                
                # 3. 刪除群組成員關聯
                cursor.execute("DELETE FROM group_members WHERE group_id = ?", (group_id,))
                
                # 4. 刪除群組基本資料
                cursor.execute("DELETE FROM groups WHERE group_id = ?", (group_id,))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Delete Group Error: {e}")
                conn.rollback()
                return False

    def delete_transaction(self, transaction_id):
        """刪除特定交易及其所有關聯的參與者紀錄"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                # 1. 刪除參與者紀錄
                cursor.execute("DELETE FROM transaction_participants WHERE transaction_id = ?", (transaction_id,))
                # 2. 刪除交易主表
                cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Delete Transaction Error: {e}")
                conn.rollback()
                return False

    def get_transaction_details(self, transaction_id):
        """獲取特定交易的完整分帳細節 (包含所有參與者金額與狀態)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. 取得基本資訊
            cursor.execute("""
                SELECT transaction_id, group_id, payer_id, amount, status, type, description, location, timestamp
                FROM transactions WHERE transaction_id = ?
            """, (transaction_id,))
            r = cursor.fetchone()
            if not r: return None
            
            tx = {"id": r[0], "group_id": r[1], "payer": r[2], "amount": r[3], "status": r[4], 
                "type": r[5], "desc": r[6], "loc": r[7], "time": r[8]}
            
            # 2. 取得所有參與者詳情
            cursor.execute("""
                SELECT user_id, owed_amount, status, settled_at 
                FROM transaction_participants WHERE transaction_id = ?
            """, (transaction_id,))
            tx["participants"] = [{"user_id": p[0], "amount": p[1], "status": p[2], "settled_at": p[3]} for p in cursor.fetchall()]
            
            return tx

    def repay_transaction(self, group_id, tx_id, debtor_id, creditor_id, amount):
        """欠款人針對單筆帳單進行還款：建立還款紀錄並標記原帳單為已結算"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                now = datetime.now()
                # 1. 建立還款交易主表
                s_id = f"repay_{now.strftime('%Y%m%d%H%M%S')}_{random.randint(100, 999)}"
                cursor.execute("""
                    INSERT INTO transactions (transaction_id, group_id, payer_id, amount, status, type, description, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (s_id, group_id, debtor_id, amount, TransactionStatus.SETTLED.name,
                      TransactionType.SETTLEMENT.name, f"手動還款：{debtor_id} 還款給 {creditor_id}", now))

                # 2. 還款交易參與者：收款人
                cursor.execute("""
                    INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status, settled_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (s_id, creditor_id, amount, TransactionStatus.SETTLED.name, now))

                # 3. 還款交易參與者：付款人自己
                cursor.execute("""
                    INSERT INTO transaction_participants (transaction_id, user_id, owed_amount, status, settled_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (s_id, debtor_id, 0, TransactionStatus.SETTLED.name, now))

                # 4. 將原帳單中該欠款人的狀態更新為 SETTLED
                cursor.execute("""
                    UPDATE transaction_participants SET status = ?, settled_at = ?
                    WHERE transaction_id = ? AND user_id = ?
                """, (TransactionStatus.SETTLED.name, now, tx_id, debtor_id))

                # 5. 若原帳單所有參與者皆已結算，也一併更新主表狀態
                cursor.execute("""
                    SELECT COUNT(*) FROM transaction_participants
                    WHERE transaction_id = ? AND status != ?
                """, (tx_id, TransactionStatus.SETTLED.name))
                remaining = cursor.fetchone()[0]
                if remaining == 0:
                    cursor.execute("UPDATE transactions SET status = ? WHERE transaction_id = ?",
                                   (TransactionStatus.SETTLED.name, tx_id))

                conn.commit()
                return True
            except Exception as e:
                print(f"Repay Transaction Error: {e}")
                conn.rollback()
                return False

    def generate_group_bill_summary(self, group_id):
        """生成群組當前債務結算的動態摘要文字"""
        balances = self.get_group_balances(group_id)
        if not balances:
            return "目前帳目已全部結清，暫無待處理債務。"

        summary = f"【群組帳單摘要】\n群組 ID: {group_id}\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        summary += "-" * 30 + "\n"
        
        # 應收與應付明細
        creditors = {u: amt for u, amt in balances.items() if amt > 0}
        debtors = {u: abs(amt) for u, amt in balances.items() if amt < 0}
        
        if creditors:
            summary += " [應收款項]\n"
            for u, amt in creditors.items():
                summary += f"  · {u}: +${amt}\n"
        
        if debtors:
            summary += "\n [待付款項]\n"
            for u, amt in debtors.items():
                summary += f"  · {u}: -${amt}\n"
        
        # 建議結算路徑 (使用簡易簡化模式)
        summary += "\n [建議還款路徑]\n"
        plan = []
        d_list = sorted(debtors.items(), key=lambda x: x[1], reverse=True)
        c_list = sorted(creditors.items(), key=lambda x: x[1], reverse=True)
        
        d_idx, c_idx = 0, 0
        temp_d = [list(x) for x in d_list]
        temp_c = [list(x) for x in c_list]
        
        while d_idx < len(temp_d) and c_idx < len(temp_c):
            pay_amt = min(temp_d[d_idx][1], temp_c[c_idx][1])
            if pay_amt > 0:
                summary += f"  · {temp_d[d_idx][0]} -> 轉帳 ${pay_amt} 給 {temp_c[c_idx][0]}\n"
            temp_d[d_idx][1] -= pay_amt
            temp_c[c_idx][1] -= pay_amt
            if temp_d[d_idx][1] == 0: d_idx += 1
            if temp_c[c_idx][1] == 0: c_idx += 1
            
        summary += "\n請各位成員確認後，於系統內進行「確認」與「還款」操作。"
        return summary

    def get_notification_message(self, tx_id):
        """生成針對特定交易的催帳/通知文字"""
        details = self.get_transaction_details(tx_id)
        if not details: return "交易資訊不存在。"
        
        msg = f"【mysalf 帳務提醒】\n"
        msg += f"項目：{details['desc'] or '未命名支出'}\n"
        msg += f"金額：${details['amount']}\n"
        msg += f"付款人：{details['payer']}\n"
        msg += f"日期：{details['time']}\n"
        msg += "-" * 20 + "\n"
        
        pending = [p for p in details['participants'] if p['status'] == TransactionStatus.PENDING.name]
        if pending:
            names = ", ".join([p['user_id'] for p in pending])
            msg += f" 請以下成員盡速確認或支付：\n{names}\n"
        else:
            msg += " 此筆交易所有參與者已確認。"
            
        return msg
