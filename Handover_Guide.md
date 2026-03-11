# 🤝 專案開發交接指南 (Handover Guide)

歡迎加入 **Split-it-Smart** 開發團隊！為了讓您快速上手，請參考以下資訊。

## 1. 您需要取得的資料 (Handover Checklist)
請確保您已從夥伴處取得以下內容：
*   **完整原始碼**：整個 `mysalf/` 資料夾。
*   **開發環境**：
    - Python 3.10+
    - 必要套件：`pip install customtkinter pillow qrcode`
*   **資料庫檔案**：`data/accounting.db` (內含基礎資料結構)。

## 2. 專案構造 (Project Structure)
專案已進行模組化拆分，請根據您的角色在指定目錄工作：

```text
mysalf/
├── core/               # 後端邏輯
│   ├── base.py         # 資料庫連線 (基礎)
│   ├── personal_service.py # 個人功能 (角色 A)
│   ├── group_service.py    # 群組功能 (角色 B)
│   └── main.py         # 核心入口 (Facade)
├── ui/                 # 前端界面
│   ├── personal/       # 個人頁面 (角色 A)
│   ├── group/          # 群組頁面 (角色 B)
│   └── AccountingGUI.py # 主程式執行檔
└── data/               # 資料庫與資源
```

## 3. 分工說明 (Division of Labor)
*   **角色 A (個人部分)**：
    - 負責 `ui/personal/` 內的介面。
    - 負責 `core/personal_service.py` 內的好友與個人債務邏輯。
*   **角色 B (群組部分)**：
    - 負責 `ui/group/` 內的介面。
    - 負責 `core/group_service.py` 內的群組與交易分帳邏輯。

## 4. 如何協作 (Git Workflow)
本專案已初始化 Git，請遵循以下流程：

### ⚡️ 首次連結 (一鍵自動化 - 推薦)
若您要在 GitHub/GitLab 建立遠端倉庫，只需執行根目錄的 **`setup_git.bat`**：
1. 依照提示貼上您的遠端倉庫網址。
2. 程式會自動完成 `remote add`、`branch` 切換與 `push` 操作。

### 🔧 手動連結 (進階)
若您偏好手動操作，請執行：
```bash
git remote add origin <您的遠端倉庫網址>
git branch -M master
git push -u origin master
```

### 🔄 如何獲取夥伴更新 (推薦)
直接執行根目錄的 **`sync_latest.bat`**。
它會自動幫您：
1. 從 GitHub 拉取最新代碼。
2. 自動更新您的本地資料庫結構 (對齊 `schema.sql`)。

### 🔄 手動同步流程 (日常開發)
1. **更新代碼**：`git pull origin master`
2. **同步資料庫**：執行 `update_db.bat`
3. **提交變更**：`git add .` -> `git commit -m "描述變更"`
4. **推送到雲端**：`git push origin master`

### 🗄️ 同步資料庫結構 (Database Sync)
當獲取最新的 `doc/schema.sql` 後，請執行根目錄的 **`update_db.bat`**。
這會自動將 SQL 中的新表格或新欄位套用到您的本地資料庫。

## 5. 如何執行 (How to Run)
### ⚡️ 一鍵執行 (推薦)
在 Windows 環境下，直接點擊根目錄的 **`run.bat`** 即可啟動程式。
(註：此批次檔會調用 `run.py` 來確保跨平台編碼正確並檢查環境變數。)
在 `mysalf/` 目錄下執行：
```bash
python ui/AccountingGUI.py
```

---
*祝開發順利！如果有任何邏輯問題，請查閱 `core/main.py` 中的繁體中文註解。*


📂 專案根目錄 (mysalf/)
run.bat (一鍵啟動)：這是最推薦的執行方式。直接雙擊它，它會透過 run.py 檢查您的 Python 環境並啟動程式，完美避免亂碼問題。
setup_git.bat (一鍵連線 Git)：如果您或夥伴需要連結到 GitHub，執行這個檔案並貼上網址即可完成設置。
Handover_Guide.md：專為合作夥伴準備的「交接指南」，裡面有分工說明與操作教學。
.gitignore：設定了自動排除資料庫與緩存，確保您們 Git 協作時不會互相衝突。
📂 核心邏輯層 (core/) —— 系統的「大腦」
我將原本龐大的 main.py 拆分成了功能獨立的模組：

base.py：資料庫的最底層連線與表格初始化邏輯。
models.py：定義了交易的狀態（待驗證、已結清）與類型（消費、還款）。
personal_service.py (角色 A 負責)：處理好友清單、個人債務摘要與 QR 碼生成。
group_service.py (角色 B 負責)：處理群組管理、成員維護與核心的「分帳演算法」。
main.py：作為統一入口 (Facade)，整合上述所有功能，確保 UI 端調用方式不變。
📂 介面展示層 (ui/) —— 系統的「外觀」
UI 也按照功能進行了分類：

personal/ (角色 A 負責)：包含個人的帳單摘要頁面與好友管理頁面。
group/ (角色 B 負責)：包含群組的即時動態牆與共同支出管理。
components/：存放通用的組件（如登入畫面、專用的對話框）。
AccountingGUI.py：主程式框架，負責側邊欄導航與各頁面的切換整合。
📂 數據與文件層 (data/ & doc/)
data/：存放最重要的資料庫檔案 accounting.db 以及產生的 QR 碼圖檔。
doc/：存放資料庫的原始 SQL 結構說明 (schema.sql)。
總結：現在 mysalf 不僅外觀整潔，內部邏輯也實現了「個人」與「群組」的完全解耦，這讓您與夥伴在開發時，基本上只要在各自負責的資料夾下工作，就不會互相干擾。

mysalf/
├── run.bat              # ✅ 一鍵啟動程式 (Windows 推薦)
├── run.py               # 啟動腳本核心邏輯
├── setup_git.bat        # ✅ 一鍵連結 GitHub 設置工具
├── setup_git.py         # Git 設置邏輯
├── Handover_Guide.md     # 🤝 交接指南與開發者說明書
├── .gitignore           # Git 忽略設定 (排除資料庫與緩存)
├── DEVELOPMENT_GUIDE.md # 開發參考文件
├── features.md          # 功能列表
├── 計劃書.txt            # 原始專案計畫
│
├── core/                # 🧠 核心邏輯層 (大腦)
│   ├── base.py          # 資料庫基礎連線
│   ├── models.py        # 數據模型定義 (Enum)
│   ├── personal_service.py # 個人與好友功能 (Person A)
│   ├── group_service.py    # 群組與分帳功能 (Person B)
│   └── main.py          # 核心總入口 (Facade)
│
├── ui/                  # 🎨 介面展示層 (外觀)
│   ├── AccountingGUI.py  # 主程式框架與導航
│   ├── personal/        # 個人專屬頁面 (Person A)
│   │   ├── personal_frame.py
│   │   └── friends_frame.py
│   ├── group/           # 群組專屬頁面 (Person B)
│   │   └── group_frame.py
│   └── components/      # 共用元件 (登入、對話框)
│       └── common.py
│
├── data/                # 💾 數據存儲層
│   ├── accounting.db    # 正式 SQLite 資料庫
│   └── (QR 碼圖檔)
│
└── doc/                 # 📄 文檔層
    └── schema.sql       # 資料庫結構腳本
