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

def init_git_config():
    """初始化 Git 編碼設定，防止中文亂碼"""
    root_dir, _, _ = get_base_dirs()
    print("[系統] 正在優化 Git 環境編碼...")
    run_command("git config i18n.commitencoding utf-8", cwd=root_dir)
    run_command("git config i18n.logoutputencoding utf-8", cwd=root_dir)

def get_base_dirs():
    """取得專案各個核心目錄的絕對路徑"""
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    users_dir = os.path.dirname(tools_dir)
    root_dir = os.path.dirname(users_dir)
    server_dir = os.path.join(root_dir, "server")
    return root_dir, users_dir, server_dir

def get_db_path():
    _, users_dir, _ = get_base_dirs()
    return os.path.join(users_dir, "shared", "data", "accounting.db")

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
            cursor.execute("ALTER TABLE groups ADD COLUMN join_code TEXT")
            
        cursor.execute("PRAGMA table_info(transactions)")
        tx_cols = [c[1] for c in cursor.fetchall()]
        if "description" not in tx_cols:
            cursor.execute("ALTER TABLE transactions ADD COLUMN description TEXT")
        if "location" not in tx_cols:
            cursor.execute("ALTER TABLE transactions ADD COLUMN location TEXT")
        if "category" not in tx_cols:
            cursor.execute("ALTER TABLE transactions ADD COLUMN category TEXT DEFAULT 'OTHER'")
            
        conn.commit()
        conn.close()
        print("[完成] 資料庫結構已是最新版本。")
        return True
    except Exception as e:
        print(f"[錯誤] 資料庫更新失敗: {e}")
        return False

def run_tests():
    """執行自動化單元測試"""
    _, users_dir, _ = get_base_dirs()
    print("\n[功能] 正在執行自動化單元測試 (pytest)...")
    success = run_command("python -m pytest tests/test_debt_system.py", cwd=users_dir)
    if success:
        print("\n[成功] 所有核心測試均已通過！")
    else:
        print("\n[警告] 部分測試未通過。")

def start_dev_server():
    """啟動 API 伺服器"""
    _, _, server_dir = get_base_dirs()
    server_bat = os.path.join(server_dir, "run_online_A.bat")
    if os.path.exists(server_bat):
        print("\n[功能] 正在啟動 API 伺服器...")
        run_command(f'start cmd /k "{server_bat}"', cwd=server_dir)
    else:
        print(f"[錯誤] 找不到伺服器啟動檔: {server_bat}")

def upload_changes():
    root_dir, _, _ = get_base_dirs()
    print("\n[功能] 正在準備上傳變更到伺服器...")
    run_command("git status -s", cwd=root_dir)
    
    msg = input("\n請輸入提交訊息 (Commit Message): ").strip()
    if not msg:
        print("[取消] 未輸入訊息。")
        return

    # 關鍵修正：使用暫存檔來傳遞訊息，徹底解決 Windows 下的中文亂碼問題
    msg_file = os.path.join(root_dir, "temp_commit_msg.txt")
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write(msg)

    run_command("git add .", cwd=root_dir)
    # 使用 -F 參數讀取 UTF-8 檔案
    if run_command(f'git commit -F "{msg_file}"', cwd=root_dir):
        # 推送至遠端 master (確保與 GitHub 同步)
        if run_command("git push origin master", cwd=root_dir):
            print("\n[成功] 變更已推送到 GitHub master 分支。")
    
    # 清理暫存檔
    if os.path.exists(msg_file):
        os.remove(msg_file)

def sync_latest():
    root_dir, _, _ = get_base_dirs()
    print("\n[功能] 正在同步最新版本...")
    if run_command("git pull origin master", cwd=root_dir):
        print("\n[成功] 程式碼同步完成。")
        update_db()

def main_menu():
    init_git_config()  # 啟動時自動初始化環境
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*45)
        print("   Group Ledger 全功能維護中心 (V2.1 - UTF8)")
        print("="*45)
        print(" 1. 更新資料庫結構 (Database Update)")
        print(" 2. 執行自動化測試 (Run Unit Tests)")
        print(" 3. 啟動開發伺服器 (Start API Server)")
        print(" 4. 上傳變更至 GitHub (Git Push master)")
        print(" 5. 拉取最新遠端版本 (Git Pull master)")
        print(" 6. 退出工具")
        print("="*45)
        
        choice = input("\n請選擇操作項目 (1-6): ").strip()
        
        if choice == '1':
            update_db()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            start_dev_server()
        elif choice == '4':
            upload_changes()
        elif choice == '5':
            sync_latest()
        elif choice == '6':
            print("系統已安全退出。")
            break
        else:
            print("無效的選擇，請重新輸入。")
        
        input("\n按 Enter 鍵繼續...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n[已中斷] 使用者強制結束作業。")
