import sqlite3
import os

class BaseService:
    """基礎服務類別：提供資料庫連接與初始化功能"""
    def __init__(self, db_path=None):
        if db_path is None:
            # 檔案位於 app/shared/base_service.py，資料庫位於 app/shared/data/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, "data", "accounting.db")
        else:
            self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """取得資料庫連接"""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """建立資料庫表結構 (如果不存在)"""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. 群組表 (Groups)：儲存群組基本資料
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    group_id TEXT PRIMARY KEY,    -- 群組唯一識別碼
                    name TEXT NOT NULL,           -- 群組名稱
                    join_code TEXT,               -- 加入代碼 (6位數英數)
                    budget INTEGER DEFAULT 0      -- 總預算金額
                )
            """)
            
            # 2. 群組成員表 (Group Members)：多對多關聯表，紀錄誰在哪個群組
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_members (
                    group_id TEXT,                -- 所屬群組 ID
                    user_id TEXT,                 -- 使用者 ID
                    PRIMARY KEY (group_id, user_id)
                )
            """)
            
            # 3. 交易主表 (Transactions)：紀錄每一筆帳單的總覽
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY, -- 帳單唯一識別碼
                    group_id TEXT,                   -- 所屬群組 (若是私下轉帳則為 'PERSONAL')
                    payer_id TEXT,                   -- 代墊人 / 付款人
                    amount INTEGER,                  -- 帳單總金額 (整數，適用於台幣)
                    status TEXT,                     -- 帳單狀態 (PENDING/CONFIRMED/SETTLED/REJECTED)
                    type TEXT DEFAULT 'EXPENSE',     -- 交易類型 (EXPENSE 支出 / SETTLEMENT 還款)
                    category TEXT DEFAULT 'OTHER',   -- 帳單分類 (飲食、交通等)
                    description TEXT,                -- 帳單備註/名目
                    location TEXT,                   -- 發生地點 (註：在系統結清時會被借用存放關聯的舊帳單ID)
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP -- 發生時間
                )
            """)
            
            # 4. 交易參與者表 (Transaction Participants)：紀錄每筆帳單中「誰該付多少錢」
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_participants (
                    transaction_id TEXT,          -- 對應的主帳單 ID
                    user_id TEXT,                 -- 參與者/欠款人 ID
                    owed_amount INTEGER,          -- 該參與者應分攤/欠款的金額
                    status TEXT DEFAULT 'PENDING',-- 該參與者的確認狀態
                    settled_at DATETIME,          -- 該筆債務結清的時間 (未結清為 NULL)
                    PRIMARY KEY (transaction_id, user_id)
                )
            """)
            
            # 5. 好友名單表 (Friends)：紀錄私下好友關係 (無關群組的記帳)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS friends (
                    user_id TEXT,                 -- 使用者本身
                    friend_id TEXT,               -- 朋友 ID
                    PRIMARY KEY (user_id, friend_id)
                )
            """)
            conn.commit()
