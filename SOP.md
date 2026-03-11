# 🚀 Split-it-Smart 開發者開工 SOP

歡迎加入開發團隊！請按照以下標準作業流程 (SOP) 配置您的環境並開始協作。

---

## 🛠️ 第一階段：環境配置 (Environment Setup)
*一次性操作*

1.  **安裝 Python**：確保您的電腦已安裝 [Python 3.10+](https://www.python.org/)。
2.  **下載專案**：
    ```bash
    git clone https://github.com/HuangRuihong/PJ02.git
    ```
3.  **安裝必要套件**：進入 `mysalf` 資料夾後執行：
    ```bash
    pip install -r requirements.txt
    ```

---

## 🔄 第二階段：每日開工同步 (Daily Sync)
*每次開始寫代碼前執行*

1.  **一鍵同步**：雙擊根目錄的 **`sync_latest.bat`**。
    *   這會自動執行 `git pull` 獲取最新代碼。
    *   這會自動執行 `update_db.bat` 確保您的本地資料庫結構是最新的。

---

## 💻 第三階段：分工開發 (Development)
請根據您的角色在指定的資料夾內進行開發，以避免衝突。

*   **角色 A (個人功能)**：
    *   UI: `ui/personal/`
    *   邏輯: `core/personal_service.py`
*   **角色 B (群組功能)**：
    *   UI: `ui/group/`
    *   邏輯: `core/group_service.py`
    *   整合: `ui/AccountingGUI.py`

*   **測試執行**：雙擊 **`run.bat`** 即可啟動程式進行測試。

---

## 📤 第四階段：提交與分享 (Commit & Push)
*完成功能後執行*

1.  **一鍵上傳 (推薦)**：雙擊 **`upload_changes.bat`**。
    *   按照提示輸入您改了什麼，腳本會自動完成 `add` -> `commit` -> `push`。
2.  **手動上傳 (進階)**：
    *   `git add .`
    *   `git commit -m "功能名稱: 簡短描述"`
    *   `git push origin master`

---

## ⚠️ 注意事項 (Important Rules)
*   **不要提交資料庫**：`.gitignore` 已自動排除 `.db` 檔案，請勿強制上傳。
*   **資料庫變動**：若您新增了 Table 或 Column，請務必更新 **`doc/schema.sql`** 並隨代碼一同提交。
*   **保持 master 乾淨**：確保您的代碼在本地執行 `run.bat` 沒問題後再推送。

---
*祝開發順利！讓我們一起做出最棒的分帳系統！*
