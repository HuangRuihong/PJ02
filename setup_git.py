import subprocess
import os
import sys

def run_git_setup():
    print("="*50)
    print("Split-it-Smart Git 自動設置工具")
    print("="*50)

    # 1. 檢查 Git 是否初始化
    if not os.path.exists(".git"):
        print("[錯誤] 此目錄尚未初始化 Git。正在嘗試初始化...")
        subprocess.run(["git", "init"], check=True)

    # 2. 取得遠端網址
    print("\n請在下方貼上您的遠端倉庫網址 (Remote URL):")
    print("例如: https://github.com/YourName/YourRepo.git")
    remote_url = input("網址 > ").strip()

    if not remote_url.endswith(".git") and "http" not in remote_url:
        print("[警告] 網址格式看起來不太正確，請務必確認。")
    
    if not remote_url:
        print("[取消] 未輸入網址，終止操作。")
        return

    # 3. 執行連結指令
    try:
        print(f"\n[1/3] 正在移除舊有的 origin (如果有的話)...")
        subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
        
        print(f"[2/3] 正在連結遠端倉庫: {remote_url}")
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
        
        print(f"[3/3] 正在切換主分支並推送代碼...")
        subprocess.run(["git", "branch", "-M", "master"], check=True)
        
        # 這裡會觸發 Git 的登入視窗
        print("-" * 50)
        print("提示: 若彈出登入視窗，請完成 GitHub/GitLab 驗證。")
        result = subprocess.run(["git", "push", "-u", "origin", "master"])
        
        if result.returncode == 0:
            print("-" * 50)
            print("✨ 恭喜！專案已成功上傳至傳至遠端倉庫。")
        else:
            print("\n[錯誤] 推送失敗。請確認您的網址是否有誤，或是否具備寫入權限。")
            
    except Exception as e:
        print(f"\n[發生異常] {e}")

    input("\n設定完成，請按任意鍵結束...")

if __name__ == "__main__":
    run_git_setup()
