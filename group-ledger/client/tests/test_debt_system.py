import pytest
import os
import sys

# 確保能從根目錄導入模組
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), "src")
sys.path.append(src_dir)

from intelligence.debt_system import DebtSystem

import tempfile

@pytest.fixture
def system():
    """建立一個暫存檔案資料庫進行測試，確保子服務共享同一資料庫"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    sys_instance = DebtSystem(db_path=path)
    yield sys_instance
    if os.path.exists(path):
        os.remove(path)

def test_create_and_join_group(system):
    """測試建立與加入群組"""
    user1 = "Alice"
    user2 = "Bob"
    
    # Alice 建立群組
    gid, code = system.create_group_with_code(user1, "測試群組")
    assert gid is not None
    assert len(code) == 6
    
    # Bob 使用代碼加入
    success = system.join_group_by_code(user2, code)
    assert success is True
    
    # 驗證成員
    members = system.get_group_members(gid)
    assert user1 in members
    assert user2 in members

def test_transaction_lifecycle(system):
    """測試交易的完整生命週期 (提案 -> 確認 -> 結算)"""
    user1 = "Alice"
    user2 = "Bob"
    gid, _ = system.create_group_with_code(user1, "測試群組")
    system.join_group_by_code(user2, system.get_user_groups(user1)[0]['code'])
    
    # Alice 提案一筆 100 元的支出，Bob 參與平分
    tx_id = "tx_001"
    success = system.propose_transaction(
        transaction_id=tx_id,
        payer_id=user1,
        amount_float=100.0,
        participants=[user1, user2],
        group_id=gid,
        description="測試晚餐"
    )
    assert success is True
    
    # 檢查狀態是否為 PENDING
    details = system.get_transaction_details(tx_id)
    assert details['status'] == 'PENDING'
    
    # Bob 確認交易
    system.confirm_transaction(user2, tx_id)
    
    # 檢查狀態是否變為 CONFIRMED
    details = system.get_transaction_details(tx_id)
    assert details['status'] == 'CONFIRMED'
    
    # 執行結算
    plan = system.settle_debts(gid, user1)
    assert plan is not None
    assert len(plan['plan']) > 0
    assert plan['plan'][0]['from'] == user2
    assert plan['plan'][0]['to'] == user1
    assert plan['plan'][0]['amount'] == 50.0

def test_user_summary(system):
    """測試個人帳務總覽"""
    user1 = "Alice"
    user2 = "Bob"
    gid, _ = system.create_group_with_code(user1, "群組")
    system.join_group_by_code(user2, system.get_user_groups(user1)[0]['code'])
    
    # Alice 付 200，兩人平分 -> Bob 欠 Alice 100
    system.propose_transaction("tx_1", user1, 200, [user1, user2], gid)
    system.confirm_transaction(user2, "tx_1")
    
    summary = system.get_user_summary(user2)
    assert summary[user1] == -100.0 # Bob 應付 Alice 100
