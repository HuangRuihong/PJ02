# 🛠️ Split-it-Smart 前置作業 SOP (工程配置與同步)

本手冊引導開發者在「開始寫程式前」完成必要的環境設定與進度同步。

---

## 1. 環境配置 (Environment Setup)
*一次性操作：新成員加入時執行*

1.  **安裝 Python**：確保您的電腦已安裝 [Python 3.10+](https://www.python.org/)。
2.  **正式下載專案**：
    在桌面打開終端機，執行以下指令 (⚠️ 請勿下載 ZIP 壓縮檔)：
    ```bash
    git clone https://github.com/HuangRuihong/PJ02.git
    ```
3.  **安裝必要套件**：進入 `mysalf` 資料夾後執行：
    ```bash
    pip install -r requirements.txt
    ```

---

## 2. 每日開工同步 (Daily Sync)
*例行操作：每次開始寫代碼前務必執行*

1.  **一鍵同步進度**：雙擊根目錄的 **`sync_latest.bat`**。
    *   **代碼更新**：自動執行 `git pull` 獲取夥伴的最新成果。
    *   **結構更新**：自動執行 `update_db.bat` 對齊資料庫最新的 `schema.sql`。

---

## ⚠️ 注意事項 
*   **不要下載 ZIP**：若使用 ZIP 下載，將無法執行一鍵同步腳本。
*   **同步優先**：先同步、後開發，能有效減少代碼衝突。

---
*前置作業完成後，即可依照「完成後作業 SOP」開始開發與上傳成果。*
