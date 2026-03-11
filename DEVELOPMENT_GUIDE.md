# 債務管理系統開發順序與結構指南 (Development Roadmap & Structure Guide)

## 專案定位：室友/朋友圈的非同步記帳系統
本系統專為熟人社交圈（如室友、死黨）設計，核心在於**「非同步提案」**與**「共識確認」**，確保每一筆分帳都經過相關人的認可，避免帳務爭議。

---

## 一、 開發順序 (Development Order)

我們採取了「自底向上 (Bottom-Up)」的工程路徑，優先確保資料的正確性與安全性：

### 1. 核心實體定義 (Core Entities)
- 定義 `Transaction` 與 `TransactionStatus` 枚舉（Pending, Confirmed, Rejected）。
- 確立交易的基礎狀態機流轉邏輯。

### 2. 資料持久化與安全性 (Data Persistence & Atomicity)
- **資料庫選擇**：採用 SQLite 以實現零配置、單檔案存儲。
- **Schema 設計**：建立 `groups`, `transactions`, `participants` 表，並規範 SQL 變更必須記錄於 `doc/`。
- **事務保護 (Atomicity)**：實作 `propose_transaction` 的原子性寫入，防止產生孤兒帳單。
- **精度處理 (Precision)**：全面使用「分 (Integer)」作為金額儲存單位，杜絕浮點數運算誤差。

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
├── core/           # [核心段落] 系統大腦
│   └── main.py     # 包含 DebtSystem 類別，負責所有業務處理與資料庫互動
│
├── data/           # [資料段落] 持久化存儲
│   └── accounting.db # 生產環境資料庫檔案
│
├── ui/             # [展示段落] 使用者介面
│   └── AccountingGUI.py # 預留位，用於開發桌面版圖形界面 (CustomTkinter)
│
├── doc/            # [文件段落] 工程規範
│   └── schema.sql  # 資料庫結構定義與變更紀錄
│
└── test/           # [驗證段落] 品質保證
    ├── test_main.py         # 核心邏輯整合測試
    └── test_db_atomicity.py # 資料庫原子性與精度專項測試
```

---

## 三、 後續開發重點 (Next Steps)

1. **UI 串接**：將 `core/main.py` 的 API 對接到桌面應用程式。
2. **向量時鐘 (Vector Clock)**：準備應對未來可能的分散式同步情境。
3. **債務簡化演算法**：在「保留原始債權」的基礎上，提供組內債務抵銷建議。
