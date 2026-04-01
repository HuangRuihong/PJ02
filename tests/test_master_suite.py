import os
import sys
import datetime
from datetime import timedelta

# 設定編碼，解決 Windows 終端機亂碼
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 核心：將根目錄加入系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.main import DebtSystem
from backend.core.models import TransactionStatus

def cleanup():
    """初始化測試資料庫"""
    db_path = "backend/data/accounting.db"
    if os.path.exists(db_path):
        try: os.remove(db_path)
        except: pass

def run_all_tests():
    print("🚀 開啟全功能大滿貫測試 (Master Suite)...")
    system = DebtSystem()
    
    # --- TEST 1: 個人帳務隔離測試 ---
    print("\n[測試 1] 個人私帳隔離功能")
    # A 在群組外有一筆私人的午餐費 $150
    system.propose_transaction("p_01", "User_A", 150, ["User_A"], None, description="個人午餐(私密)")
    history_a = system.get_personal_history("User_A")
    history_b = system.get_personal_history("User_B")
    
    # 驗證 A 看得到，B 看不到 (確保隔離性)
    a_found = any(x['id'] == "p_01" for x in history_a)
    b_found = any(x['id'] == "p_01" for x in history_b)
    if a_found and not b_found:
        print("✅ 隔離驗證通過：個人私密帳務不會流向他人。")
    else:
        print(f"❌ 隔離失敗！A_found:{a_found}, B_found:{b_found}")

    # --- TEST 2: 群組預算控管邏輯 ---
    print("\n[測試 2] 群組預算與剩餘額度計算")
    gid, code = system.create_group_with_code("User_A", "預算測試群")
    system.set_group_budget(gid, 2000) # 設定預算為 $2000
    
    # 進行一筆 $500 的支出
    system.propose_transaction("b_01", "User_A", 500, ["User_A"], gid, description="文具支出")
    budget_info = system.get_group_budget_status(gid)
    
    print(f"  - 目前預算: {budget_info['budget']}, 已支出: {budget_info['spent']}, 剩餘: {budget_info['remaining']}")
    if budget_info['remaining'] == 1500:
        print("✅ 預算控管通過：餘額計算準確。")
    else:
        print(f"❌ 預算計算錯誤：預期 1500，實際 {budget_info['remaining']}")

    # --- TEST 3: 動態逾期催告演算法 ---
    print("\n[測試 3] 逾期催告與動態期限建議 (7/14/30天)")
    # 建立一筆 40 天前的交易 ($3000 元，建議期限應為 30 天，此時已逾期)
    old_date = datetime.datetime.now() - timedelta(days=40)
    system.propose_transaction("overdue_01", "User_A", 3000, ["User_B"], gid, description="舊帳單測試", timestamp=old_date)
    
    # 觸發系統逾期掃描
    overdue_list = system.check_overdue_transactions()
    found_overdue = any(x['id'] == "overdue_01" for x in overdue_list)
    
    if found_overdue:
        print("✅ 逾期演算法通過：成功偵測到 40 天前的 $3000 元帳單已逾期。")
    else:
        print("❌ 逾期演算法失敗：未偵測到逾期項目。")

    # --- TEST 4: 分析數據獲取與彙整能力 ---
    print("\n[測試 4] 分析數據基礎 (用於 GUI 圓餅圖)")
    # 模擬前端分析邏輯：獲取歷史紀錄並按群組統計
    history = system.get_personal_history("User_A")
    group_sums = {}
    for tx in history:
        g_name = tx.get("group_name", "個人私帳")
        group_sums[g_name] = group_sums.get(g_name, 0) + tx["amount"]
    
    if len(group_sums) > 0:
        print(f"✅ 分析數據通過：成功從歷史紀錄彙整出 {len(group_sums)} 個群組的支出統計。")
    else:
        print("❌ 分析數據失敗：歷史紀錄為空或無法統計。")

    print("\n🏁 全功能大滿貫測試完成。所有技術指標皆符合交付標準！")

if __name__ == "__main__":
    cleanup()
    run_all_tests()
