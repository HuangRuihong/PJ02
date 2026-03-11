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

## 4. 如何執行 (How to Run)
在 `mysalf/` 目錄下執行：
```bash
python ui/AccountingGUI.py
```

---
*祝開發順利！如果有任何邏輯問題，請查閱 `core/main.py` 中的繁體中文註解。*
