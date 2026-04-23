import enum

class TransactionStatus(enum.Enum):
    """交易狀態枚舉：定義交易在系統中的生命週期"""
    PENDING = "待驗證"      # 剛提出，等待相關參與者確認
    CONFIRMED = "已確認"    # 所有參與者已確認，正式生效
    REJECTED = "已拒絕"     # 被參與者拒絕（如金額有誤）
    SETTLED = "已結清"      # 款項已實際清償

    @classmethod
    def get_ui_info(cls, status_name):
        """統一全系統交易狀態的 UI 顯示 (Person A 優化：降低 UI 耦合度)"""
        mapping = {
            cls.PENDING.name:   ("#e67e22", "待確認"),
            cls.CONFIRMED.name: ("#2ecc71", "已確認"),
            cls.SETTLED.name:   ("#7f8c8d", "已結清"),
            cls.REJECTED.name:  ("#e74c3c", "有誤"),
        }
        default_info = ("#34495e", status_name)
        return mapping.get(status_name, default_info)

class TransactionType(enum.Enum):
    """交易類型枚舉：區分一般消費與還款行為"""
    EXPENSE = "消費"        # 一般購物、聚餐支出
    SETTLEMENT = "還款"     # 債務結清、轉帳還款
    REPAY_REQUEST = "還款申請" # 結清申請
