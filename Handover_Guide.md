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
1. **複製專案**：
   ```bash
   git clone <專案網址>
   ```
2. **開發流程**：
   - 建立分支：`git checkout -b <您的名字>-<功能名>`
   - 提交變更：`git add .` -> `git commit -m "描述變更"`
   - 推送分支：`git push origin <分支名>`
3. **注意事項**：
   - `.gitignore` 已設定排除 `accounting.db`，請手動透過其他方式交換資料庫內容，或各自維護本地測試數據。

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
