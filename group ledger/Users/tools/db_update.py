import sqlite3
import os
import sys

def get_db_path():
    # 檔案位於 app/tools/，要找 app/shared/data/accounting.db
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "shared", "data", "accounting.db")

def update_schema():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        print("Please run the main application first to initialize the database.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 檢查並修正遺漏的欄位 (例如 description, location, join_code)
    try:
        # 1. groups 表加入 join_code
        cursor.execute("PRAGMA table_info(groups)")
        cols = [c[1] for c in cursor.fetchall()]
        if "join_code" not in cols:
            print("正在更新 groups 表：加入 join_code 欄位...")
            cursor.execute("ALTER TABLE groups ADD COLUMN join_code TEXT")
        if "budget" not in cols:
            print("正在更新 groups 表：加入 budget 欄位...")
            cursor.execute("ALTER TABLE groups ADD COLUMN budget INTEGER DEFAULT 0")
            
        # 2. transactions 表加入 description, location
        cursor.execute("PRAGMA table_info(transactions)")
        cols = [c[1] for c in cursor.fetchall()]
        if "description" not in cols:
            print("正在更新 transactions 表：加入 description 欄位...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN description TEXT")
        if "location" not in cols:
            print("正在更新 transactions 表：加入 location 欄位...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN location TEXT")
        if "category" not in cols:
            print("正在更新 transactions 表：加入 category 欄位...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN category TEXT DEFAULT 'OTHER'")
            
        conn.commit()
        print("[OK] 資料庫結構校驗完成。")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] 更新資料庫時發生錯誤：{e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
