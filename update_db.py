import sqlite3
import os

def update_database():
    print("="*50)
    print("資料庫結構同步工具 🗄️")
    print("="*50)

    db_path = os.path.join("data", "accounting.db")
    sql_path = os.path.join("doc", "schema.sql")

    # 檢查檔案是否存在
    if not os.path.exists(sql_path):
        print(f"[錯誤] 找不到 SQL 結構檔: {sql_path}")
        return

    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))

    try:
        print(f"[1/2] 正在讀取 {sql_path}...")
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        print(f"[2/2] 正在套用變更至 {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 執行 SQL 腳本 (支援一次執行多個語句)
        cursor.executescript(sql_script)
        
        conn.commit()
        conn.close()
        print("-" * 50)
        print("✨ 資料庫結構已成功同步至最新狀態！")
        
    except sqlite3.Error as e:
        print(f"\n[資料庫錯誤] {e}")
    except Exception as e:
        print(f"\n[發生異常] {e}")

    input("\n處理完成，請按任意鍵結束...")

if __name__ == "__main__":
    update_database()
