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
            # 1. 群組表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    group_id TEXT PRIMARY KEY, 
                    name TEXT NOT NULL,
                    join_code TEXT,
                    budget INTEGER DEFAULT 0
                )
            """)
            # 2. 群組成員表
            cursor.execute("CREATE TABLE IF NOT EXISTS group_members (group_id TEXT, user_id TEXT, PRIMARY KEY (group_id, user_id))")
            # 3. 交易主表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    group_id TEXT,
                    payer_id TEXT,
                    amount INTEGER,
                    status TEXT,
                    type TEXT DEFAULT 'EXPENSE',
                    category TEXT DEFAULT 'OTHER',
                    description TEXT,
                    location TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 4. 交易參與者表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_participants (
                    transaction_id TEXT,
                    user_id TEXT,
                    owed_amount INTEGER,
                    status TEXT DEFAULT 'PENDING',
                    settled_at DATETIME,
                    PRIMARY KEY (transaction_id, user_id)
                )
            """)
            conn.commit()
