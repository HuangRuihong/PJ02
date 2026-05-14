import sys
import os
import argparse

# 將專案路徑與 src 加入系統路徑，確保模組引用正確
current_dir = os.path.dirname(os.path.abspath(__file__)) # scripts/
project_root = os.path.dirname(current_dir)             # client/
src_dir = os.path.join(project_root, "src")

sys.path.append(current_dir)
sys.path.append(src_dir)

def auto_install_dependencies():
    """自動檢查並安裝 requirements.txt 中的套件"""
    req_path = os.path.join(current_dir, "requirements.txt")
    if os.path.exists(req_path):
        import subprocess
        print("   [System] 正在檢查必要套件 (這可能需要一點時間)...")
        try:
            # 使用 -q 進行靜默安裝，避免過多日誌干擾
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path, "-q"])
            print("   [System] 套件檢查完成。")
        except Exception as e:
            print(f"   [警告] 自動安裝套件時發生錯誤: {e}")
            print("   [提示] 請手動執行：pip install -r requirements.txt")

# 在匯入任何可能失敗的外部模組前先執行安裝
auto_install_dependencies()

try:
    # AccountingGUI 模組位於根目錄
    from main_gui import AccountingGUI
except ImportError as e:
    print(f" 錯誤：找不到主介面模組或缺少套件 ({e})。")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split-it-Smart (Group Ledger) 啟動程式")
    parser.add_argument("--host", type=str, help="中央伺服器位址 (如 http://127.0.0.1:8000)")
    args = parser.parse_args()

    print("==========================================")
    print("   Split-it-Smart (Group Ledger) starting...")
    print(f"   Mode: {'Network' if args.host else 'Local'}")
    
    system = None
    if args.host:
        try:
            from intelligence.network_facade import NetworkDebtSystem
            print(f"   Server address: {args.host}")
            system = NetworkDebtSystem(base_url=args.host)
        except ImportError as e:
            print(f"   [錯誤] 無法載入網路模組 ({e})")
            print("   [提示] 請確保已安裝必要套件：pip install requests python-dotenv")
            print("   將嘗試以本地模式啟動...")
            system = None
        except Exception as e:
            print(f"   [錯誤] 網路系統初始化失敗: {e}")
            system = None
    else:
        print("   Status: Offline database enabled")

    print("==========================================")
    
    # 啟動主程式
    app = AccountingGUI(system_instance=system)
    app.mainloop()
