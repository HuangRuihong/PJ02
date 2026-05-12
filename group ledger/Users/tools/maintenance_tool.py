import os
import sys
import sqlite3
import subprocess

def run_command(command, cwd=None):
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[錯誤] 執行指令時發生問題: {e}")
        return False

def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "shared", "data", "accounting.db")

def update_db():
    print("\n[功能] 正在檢查並更新資料庫結構...")
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"找不到資料庫檔案: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 取得現有欄位
        cursor.execute("PRAGMA table_info(groups)")
        group_cols = [c[1] for c in cursor.fetchall()]
        
        if "join_code" not in group_cols:
            print("-> 更新 groups 表：加入 join_code...")
            cursor.execute("ALTER TABLE groups ADD COLUMN join_code TEXT")
            
        cursor.execute("PRAGMA table_info(transactions)")
        tx_cols = [c[1] for c in cursor.fetchall()]
        
        if "description" not in tx_cols:
            print("-> 更新 transactions 表：加入 description...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN description TEXT")
        if "location" not in tx_cols:
            print("-> 更新 transactions 表：加入 location...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN location TEXT")
        if "category" not in tx_cols:
            print("-> 更新 transactions 表：加入 category...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN category TEXT DEFAULT 'OTHER'")
            
        conn.commit()
        conn.close()
        print("[完成] 資料庫結構已是最新版本。")
        return True
    except Exception as e:
        print(f"[錯誤] 資料庫更新失敗: {e}")
        return False

def upload_changes():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("\n[功能] 正在準備上傳變更到伺服器...")
    
    run_command("git status -s", cwd=root_dir)
    msg = input("\n請輸入提交訊息 (Commit Message): ").strip()
    if not msg:
        print("[取消] 未輸入訊息，取消上傳。")
        return

    run_command("git add .", cwd=root_dir)
    # 嘗試提交，若無變動則會失敗但我們會繼續嘗試推送 (以防有尚未推送的 commit)
    run_command(f'git commit -m "{msg}"', cwd=root_dir)
    
    if run_command("git push origin HEAD", cwd=root_dir):
        print("\n[成功] 變更已推送到伺服器。")
    else:
        print("\n[失敗] 推送過程中發生錯誤，請檢查網路或衝突。")

def sync_latest():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("\n[功能] 正在從遠端同步最新程式碼 (git pull)...")
    
    if run_command("git pull", cwd=root_dir):
        print("\n[成功] 程式碼同步完成。")
        update_db()
    else:
        print("\n[失敗] 同步失敗，請檢查網路或 Git 衝突。")

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*40)
        print("   Group Ledger 維護工具選單")
        print("="*40)
        print(" 1. 更新資料庫結構 (Database Update)")
        print(" 2. 上傳變更至伺服器 (Git Push)")
        print(" 3. 從遠端拉取最新版本 (Git Pull)")
        print(" 4. 退出工具")
        print("="*40)
        
        choice = input("\n請選擇操作項目 (1-4): ").strip()
        
        if choice == '1':
            update_db()
        elif choice == '2':
            upload_changes()
        elif choice == '3':
            sync_latest()
        elif choice == '4':
            print("已退出。")
            break
        else:
            print("無效的選擇，請重新輸入。")
        
        input("\n按 Enter 鍵繼續...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n[已中斷] 使用者強制結束作業。")
