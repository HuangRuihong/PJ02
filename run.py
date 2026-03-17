import os
import sys
import subprocess

def run():
    print("="*50)
    print("mysalf - 多人群組本地記帳系統 啟動程式")
    print("="*50)
    
    print(f"[1/2] 正在檢查 Python 環境: {sys.version.split()[0]}")
    
    try:
        import customtkinter
        import PIL
        import qrcode
        import matplotlib
        import tkcalendar
        import schedule
    except ImportError as e:
        print(f"\n[錯誤] 缺少必要套件: {e.name}")
        print("請執行以下指令安裝：")
        print("pip install -r requirements.txt")
        input("\n請按任意鍵結束...")
        return

    print("[2/2] 正在啟動主程式 (frontend/ui/AccountingGUI.py)...")
    print("-" * 50)
    
    try:
        cmd = [sys.executable, "frontend/ui/AccountingGUI.py"]
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"\n[提示] 程式已停止執行。")
        input("\n請按任意鍵結束...")

if __name__ == "__main__":
    run()
