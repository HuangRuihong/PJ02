import sys
import os

# 將專案路徑加入系統路徑，確保模組引用正確
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from frontend.ui.AccountingGUI import AccountingGUI
except ImportError:
    print(" 錯誤：找不到前端模組，請確保在專案根目錄執行此腳本。")
    sys.exit(1)

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split-it-Smart (Group Ledger) 啟動程式")
    parser.add_argument("--host", type=str, help="中央伺服器位址 (如 http://127.0.0.1:8000)")
    args = parser.parse_args()

    print("==========================================")
    print("   Split-it-Smart (Group Ledger) starting...")
    
    if args.host:
        from backend.core.network_facade import NetworkDebtSystem
        print(f"Network Mode: Server address is {args.host}")
        system = NetworkDebtSystem(base_url=args.host)
    else:
        print("Local Mode: Offline database")
        system = None

    print("==========================================")
    app = AccountingGUI(system_instance=system)
    app.mainloop()
