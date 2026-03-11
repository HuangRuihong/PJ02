# 債務管理系統開發順序與結構指南 (Development Roadmap & Structure Guide)

## 專案定位：室友/朋友圈的非同步記帳系統
本系統專為熟人社交圈（如室友、死黨）設計，核心在於**「非同步提案」**與**「共識確認」**，確保每一筆分帳都經過相關人的認可，避免帳務爭議。

---

## 一、 開發順序 (Development Order)

我們採取了「自底向上 (Bottom-Up)」的工程路徑，優先確保資料的正確性與安全性：

### 1. 核心實體定義 (Core Entities)
- 定義 `Transaction` 與 `TransactionStatus` 枚舉（Pending, Confirmed, Rejected）。
- 構建基於 `TransactionStatus` 的非同步確認流轉邏輯（從提案到共識）。

### 2. 資料持久化與安全性 (Data Persistence & Atomicity)
- **資料庫選擇**：採用 SQLite 以實現零配置、單檔案存儲。
- **Schema 設計**：建立 `groups`, `transactions`, `participants` 表，並規範 SQL 變更必須記錄於 `doc/`。
- **事務保護 (Atomicity)**：實作 `propose_transaction` 的原子性寫入，防止產生孤兒帳單。

### 3. 業務邏輯實作 (Business Logic)
- **群組管理**：實現多租戶隔離的基礎。
- **分帳計算 (Netting)**：根據已確認交易計算成員淨餘額。
- **確認機制**：實作全體參與者確認後自動轉為正式帳單的邏輯。

### 4. 目錄結構整理 (Refactoring)
- 將專案從扁平結構轉向模組化目錄（詳見下述），確保可維護性。

---

## 二、 目錄結構與段落 (Project Structure)

```text
mysalf/
├── core/           # [核心段落] 系統大腦 (Service Oriented)
│   ├── main.py     # 整合入口 (Facade)，提供 UI 調用
│   ├── base.py     # 基礎連線與架構
│   ├── models.py   # 資料模型與枚舉
│   ├── personal_service.py # 個人/好友邏輯
│   └── group_service.py    # 群組/分帳邏輯
│
├── data/           # [資料段落] 持久化存儲
│   └── accounting.db # 正式環境資料庫
│
├── ui/             # [展示段落] 使用者介面 (Categorized)
│   ├── AccountingGUI.py # 主導航框架
│   ├── personal/   # 個人/好友視圖
│   ├── group/      # 群組協作視圖
│   └── components/ # 共用組件 (如登入、彈窗)
│
├── doc/            # [文件段落] 工程規範
│   └── schema.sql  # 資料庫結構定義
│
└── run.bat         # [便捷工具] Windows 一鍵啟動
```

---

## 三、 後續開發重點 (Next Steps)

1. **UI 串接**：將 `core/main.py` 的 API 對接到桌面應用程式。
2. **向量時鐘 (Vector Clock)**：準備應對未來可能的分散式同步情境。
3. **債務簡化演算法**：在「保留原始債權」的基礎上，提供組內債務抵銷建議。
