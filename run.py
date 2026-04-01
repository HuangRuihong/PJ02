import sys
import os

# 將專案路徑加入系統路徑，確保模組引用正確
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from frontend.ui.AccountingGUI import AccountingGUI
except ImportError:
    print("❌ 錯誤：找不到前端模組，請確保在專案根目錄執行此腳本。")
    sys.exit(1)

if __name__ == "__main__":
    print("==========================================")
    print("   Split-it-Smart (Group Ledger) 啟動中...")
    print("==========================================")
    app = AccountingGUI()
    app.mainloop()
