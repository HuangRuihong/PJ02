# 💴 Split-it-Smart (Group Ledger)

一個致力於解決多人旅行糾紛、具備三階狀態機邏輯的群組記帳與債務簡化系統。

---

## 🏗️ 系統架構 (System Architecture)

本專案採用 **Client-Server (客戶端-伺服器)** 架構，支援本地離線運作與網路同步模式。

-   **[client/](./client)**：基於 Python Tkinter 的圖形化客戶端，包含核心分帳邏輯與狀態機。
-   **[server/](./server)**：基於 Python FastAPI 的中央同步伺服器。

---

## 🚀 快速開始 (Quick Start)

### 1. 環境準備
請確保您的系統已安裝 Python 3.10+。

### 2. 啟動伺服器 (Server)
如果您需要網路同步功能：
```bash
cd server
pip install -r requirements.txt
python api_server.py
```

### 3. 啟動客戶端 (Client)
開啟另一個終端機執行：
```bash
cd client
pip install -r scripts/requirements.txt
python scripts/run_app.py
```

---

## 🛠️ 技術關鍵 (Technical Highlights)
*   **三階狀態機 (3-Stage State Machine)**：嚴謹處理債務確認流程。
*   **債務簡化演算法 (Debt Simplification)**：最小化轉帳次數。
*   **資料同步機制 (Data Sync)**：支援多裝置即時同步。

詳細開發文件請參閱：`client/doc/`
