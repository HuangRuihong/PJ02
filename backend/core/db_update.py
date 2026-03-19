import sqlite3
import os
import sys

def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "data", "accounting.db")

def update_schema():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"資料庫檔案不存在：{db_path}，將由系統啟動時自動建立。")
        return

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
            
        # 2. transactions 表加入 description, location
        cursor.execute("PRAGMA table_info(transactions)")
        cols = [c[1] for c in cursor.fetchall()]
        if "description" not in cols:
            print("正在更新 transactions 表：加入 description 欄位...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN description TEXT")
        if "location" not in cols:
            print("正在更新 transactions 表：加入 location 欄位...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN location TEXT")
            
        conn.commit()
        print("資料庫結構校驗完成。")
    except Exception as e:
        print(f"更新資料庫時發生錯誤：{e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
