import enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

class TransactionStatus(enum.Enum):
    """交易狀態枚舉：定義交易在系統中的生命週期"""
    PENDING = "待驗證"      # 剛提出，等待相關參與者確認
    CONFIRMED = "已確認"    # 所有參與者已確認，正式生效
    REJECTED = "已拒絕"     # 被參與者拒絕（如金額有誤）
    SETTLED = "已結清"      # 款項已實際清償

    @classmethod
    def get_ui_info(cls, status_name):
        mapping = {
            cls.PENDING.name:   ("#e67e22", "待確認"),
            cls.CONFIRMED.name: ("#2ecc71", "已確認"),
            cls.SETTLED.name:   ("#7f8c8d", "已結清"),
            cls.REJECTED.name:  ("#e74c3c", "有誤"),
        }
        return mapping.get(status_name, ("#34495e", status_name))

class TransactionType(enum.Enum):
    """交易類型枚舉：區分一般消費與還款行為"""
    EXPENSE = "消費"        
    SETTLEMENT = "還款"     
    REPAY_REQUEST = "還款申請"

class Category(enum.Enum):
    """消費分類：用於數據分析與過濾"""
    FOOD = ("餐飲", "🍴", "#e67e22")
    TRANSPORT = ("交通", "🚗", "#3498db")
    HOUSING = ("居住", "🏠", "#e74c3c")
    ENTERTAINMENT = ("娛樂", "🎮", "#9b59b6")
    SHOPPING = ("購物", "🛍️", "#f1c40f")
    OTHER = ("其他", "📝", "#95a5a6")

    @property
    def label(self): return self.value[0]
    @property
    def icon(self): return self.value[1]
    @property
    def color(self): return self.value[2]

@dataclass
class TransactionRecord:
    """標準化交易紀錄物件"""
    id: str
    payer_id: str
    amount: float
    group_id: str = "PERSONAL"
    status: TransactionStatus = TransactionStatus.PENDING
    tx_type: TransactionType = TransactionType.EXPENSE
    category: Category = Category.OTHER
    description: str = ""
    location: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    participants: List[str] = field(default_factory=list)
    custom_splits: Dict[str, float] = field(default_factory=dict)
