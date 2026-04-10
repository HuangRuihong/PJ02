import enum

class TransactionStatus(enum.Enum):
    """交易狀態枚舉：定義交易在系統中的生命週期"""
    PENDING = "待驗證"      # 剛提出，等待相關參與者確認
    CONFIRMED = "已確認"    # 所有參與者已確認，正式生效
    REJECTED = "已拒絕"     # 被參與者拒絕（如金額有誤）
    SETTLED = "已結清"      # 款項已實際清償

class TransactionType(enum.Enum):
    """交易類型枚舉：區分一般消費與還款行為"""
    EXPENSE = "消費"        # 一般購物、聚餐支出
    SETTLEMENT = "還款"     # 債務結清、轉帳還款
