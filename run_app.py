import sys
import os
import argparse

# 將專案路徑加入系統路徑，確保模組引用正確
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    # AccountingGUI 模組位於根目錄
    from main_gui import AccountingGUI
except ImportError as e:
    print(f" 錯誤：找不到主介面模組 ({e})。請確保在專案根目錄執行此腳本。")
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
        except ImportError:
            print("   警告：找不到網路模組，將嘗試以本地模式啟動。")
            system = None
    else:
        print("   Status: Offline database enabled")

    print("==========================================")
    
    # 啟動主程式
    app = AccountingGUI(system_instance=system)
    app.mainloop()
