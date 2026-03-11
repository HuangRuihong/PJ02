# 🤝 Split-it-Smart 專案開發交接指南

歡迎加入開發團隊！這是一份高層次的專案概覽文件，旨在幫助您理解系統架構與自動化工具流。

---

## 📖 專案願景
**Split-it-Smart** 是一個現代化的個人與群組分帳系統。專案核心目標是透過模組化的設計，實現個人帳務與群組協作的完全解耦，支持多人同步開發且不產生代碼衝突。

---

## 🏗️ 系統架構 (System Architecture)

專案採用 **Facade (門面模式)** 設計，將複雜的後端服務封裝，提供簡潔的接口給 UI 層調用。

### 🧠 核心邏輯層 (`core/`)
*   **`base.py`**：資料庫最底層連線與表格初始化邏輯。
*   **`models.py`**：定義交易狀態與類型 (Enum)。
*   **`personal_service.py` (角色 A)**：處理個人好友、債務摘要與 QR 碼。
*   **`group_service.py` (角色 B)**：處理群組管理、成員維護與分帳演算法。
*   **`main.py`**：核心總入口，對 UI 層提供統一調用。

### 🎨 介面展示層 (`ui/`)
*   **`personal/` (角色 A)**：個人與好友管理相關頁面。
*   **`group/` (角色 B)**：群組動態與共同支出管理頁面。
*   **`components/`**：存放登入、對話框等共用元件。
*   **`AccountingGUI.py`**：主程式框架、側邊欄導航與頁面切換控制。

---

## 📂 資料夾樹狀結構

```text
mysalf/
├── run.bat              # ✅ 一鍵啟動程式 (Windows 推薦)
├── sync_latest.bat      # 🔄 一鍵同步 (代碼 + 資料庫結構)
├── upload_changes.bat   # 📤 一鍵上傳成果至 GitHub
├── requirements.txt     # 📦 環境依賴配置
│
├── core/                # 🧠 核心邏輯層 (大腦)
├── ui/                  # 🎨 介面展示層 (外觀)
├── data/                # 💾 數據存儲層 (資料庫與圖片)
├── doc/                 # 📄 文檔層 (SQL Schema)
│
├── 前置作業SOP.md       # 🏁 環境配置與每日同步流程
└── 完成後作業SOP.md     # 🚀 開發規範與提交上傳流程
```

---

## 🛠️ 自動化工具箱 (Automation Tools)

為了提高效率，請多加利用以下批次檔：
*   **`run.bat`**：啟動程式。自動檢查環境並解決亂碼問題。
*   **`sync_latest.bat`**：**開工前必點**。自動執行 `pull` 與資料庫結構修正。
*   **`upload_changes.bat`**：**完工後必點**。引導式上傳 `add` -> `commit` -> `push`。
*   **`setup_git.bat`**：首次設定 GitHub 遠端連結時使用。

---

## 🚀 如何開始？

請**不要直接查閱本手冊進行操作**，請優先閱讀以下 SOP：
1.  **想配置環境或開始同步？** 請讀：[前置作業SOP.md](file:///c:/PJ02/mysalf/%E5%89%8D%E7%BD%AE%E4%BD%9C%E6%A5%ADSOP.md)
2.  **想了解如何開發與提交？** 請讀：[完成後作業SOP.md](file:///c:/PJ02/mysalf/%E5%AE%8C%E6%88%90%E5%BE%8C%E4%BD%9C%E6%A5%ADSOP.md)

---
*祝開發順利！讓我們一起做出最棒的記帳系統！*
