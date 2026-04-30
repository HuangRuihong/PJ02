# 💴 Split-it-Smart (Group Ledger)

一個致力於解決多人旅行糾紛、具備三階狀態機邏輯的群組記帳與債務簡化系統。

---

## 🚀 快速上手 (Quick Start)

### 1. 安裝環境
請確保您的電子設備已安裝所需的 Python 3.10+ 環境：
```bash
pip install -r requirements.txt
```

### 2. 啟動應用程式
在專案根目錄下直接執行以下命令即可開啟圖形化介面：
```bash
python run_app.py
```


---

---

## ✨ 核心亮點 (Project Highlights)
*   **三階狀態機代碼邏輯 (Core State Machine)**：嚴謹定義了 `PENDING` -> `CONFIRMED` -> `SETTLED` 的狀態轉換，支援**「一票否決 (REJECTED)」**與**「全員結清」**模式。
*   **視覺化狀態感知 (Status Badges)**：清單中根據交易狀態區分色塊（橘、綠、紅、灰），一目了然。
*   **UUID 全球唯一 ID**：全面解決了高頻率記帳時的時間戳衝突問題。
*   **智慧分帳邏輯**：內建自定義分帳字典、欠款管理與自動催帳訊息生成功能。

---

## 📂 目錄架構 (Project Modules)
*   **`intelligence/`** - 智慧全域債務狀態機 (State Machine) 與結算核心。
*   **`shared/`** - 共用資料模型、對話框組件及 SQLite 資料庫存放。
*   **`groups/`** - 多人群組管理與多人同步邏輯。
*   **`personal/`** - 個人支出的流水記帳與好友系統。
*   **`analysis/`** - 視覺化報表統計與日曆視圖。
*   **`auth/`** - 權限驗證與自動登入系統。
*   **`doc/`** - 完整的技術手冊、架構說明與 SQL Schema。
*   **`tools/`** - 自動化維護、上傳與資料庫遷移工具。

---

### 🎓 專題聲明
本專案為資工系實務專題研究成果，旨在探討分散式環境下的帳務一致性處理規範。
