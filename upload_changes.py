import subprocess
import sys

def run_git_upload():
    print("="*50)
    print("Split-it-Smart 代碼上傳工具")
    print("="*50)

    # 1. 檢查狀態
    print("[1/3] 正在檢查檔案變動...")
    subprocess.run(["git", "add", "."])
    
    # 2. 詢問提交訊息
    print("-" * 50)
    msg = input("請輸入本次修改的內容說明 (例如：更新了介面顏色): \n> ").strip()
    
    if not msg:
        print("\n[提示] 說明內容不能為空，上傳取消。")
        input("\n按任意鍵結束...")
        return

    # 3. 執行提交與推送
    print("-" * 50)
    print(f"[2/3] 正在記錄變更: {msg}")
    commit_res = subprocess.run(["git", "commit", "-m", msg])
    
    if commit_res.returncode != 0:
        print("\n[訊息] 沒有偵測到新的變動需要提交。")
    
    print("\n[3/3] 正在推送到 GitHub...")
    push_res = subprocess.run(["git", "push", "origin", "master"])

    if push_res.returncode == 0:
        print("\n" + "="*50)
        print("上傳成功！夥伴現在可以看見您的更動了。")
        print("="*50)
    else:
        print("\n[錯誤] 上傳失敗。請檢查網路連線或 GitHub 權限。")

    input("\n處理完成，請按任意鍵結束...")

if __name__ == "__main__":
    run_git_upload()
