# 🚀 Split-it-Smart 完成後作業 SOP (開發、提交與上傳)

本手冊引導開發者在「開發過程中」與「完成功能後」如何正確提交並分享成果。

---

## 1. 分工開發規範 (Development)

*   **角色 A (個人功能)**：`ui/personal/`, `core/personal_service.py`
*   **角色 B (群組功能)**：`ui/group/`, `core/group_service.py`, `ui/AccountingGUI.py`
*   **[NEW] 角色 S (伺服器開發)**：`backend/server/app.py`, `core/network_facade.py`

---

## 2. 功能驗證 (Verification)
*在推送前，請確保以下兩項測試皆通過：*

1.  **本地模式測試**：
    雙擊 **`run.bat`** 確認程式可正常啟動。
2.  **[NEW] 連網同步測試**：
    *   先開啟 **`start_server.bat`**。
    *   再開啟 **`run_online.bat`**。
    *   測試 API 呼叫是否正常（觀察伺服器終端機的 HTTP Logs）。

---

## 3. 提交與上傳 (Commit & Push)

1.  **一鍵自動上傳 (推薦)**：雙擊 **`upload_changes.bat`**。
2.  **手動上傳 (進階)**：
    ```bash
    git add .
    git commit -m "功能名稱: 描述修改內容"
    git push origin master
    ```

---

## 4. 核心準則 (Core Rules)
*   **[NEW] 結構同步**：若修改資料庫，必須更新 `doc/schema.sql` 與伺服器端的 `server_accounting.db`。
*   **代碼隔離**：請勿將個人測試用的 `.db` 檔案推送到 Git。
*   **通知夥伴**：完成後，請通知夥伴同步最新進度。

---
*辛苦了！您的貢獻已成功同步至 GitHub 雲端。*
