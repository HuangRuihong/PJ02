import os
import subprocess
import sys

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[錯誤] 執行指令時發生問題: {e}")
        return False

def upload():
    # 腳本在 app/tools/，專案根目錄在 ../../
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("="*40)
    print("   Group Ledger 自動化提交工具")
    print("="*40)
    
    # 1. 檢查狀態
    print("\n[1/3] 正在掃描變動檔案...")
    run_command("git status -s", cwd=root_dir)
    
    # 2. 輸入訊息
    msg = input("\n請輸入本次變更的簡短描述 (Commit Message): ").strip()
    if not msg:
        print("[取消] 必須輸入提交訊息才能上傳。")
        return

    # 3. 執行 Git 流程
    print(f"\n[2/3] 正在打包變更: {msg}...")
    if not run_command("git add .", cwd=root_dir): return
    if not run_command(f'git commit -m "{msg}"', cwd=root_dir): return
    
    print("\n[3/3] 正在推送到伺服器 (git push)...")
    if run_command("git push origin master", cwd=root_dir):
        print("\n" + "="*40)
        print("   ✅ 上傳成功！")
        print("="*40)
    else:
        print("\n[失敗] 推送過程中發生錯誤，請檢查網路或衝突。")

if __name__ == "__main__":
    try:
        upload()
    except KeyboardInterrupt:
        print("\n[已取消] 作業被使用者中斷。")
