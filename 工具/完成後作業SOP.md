# 🚀 Split-it-Smart 完成後作業 SOP (開發、提交與上傳)

本手冊引導開發者在「開發過程中」與「完成功能後」如何正確提交並分享成果。

---

## 1. 分工開發規範 (Development)
請根據您的角色在指定的資料夾內進行開發，並多加利用測試腳本。

*   **角色 A (個人功能)**：
    *   UI 頁面：`ui/personal/`
    *   後端服務：`core/personal_service.py`
*   **角色 B (群組功能)**：
    *   UI 頁面：`ui/group/`
    *   後端服務：`core/group_service.py`
    *   核心整合：`ui/AccountingGUI.py`

*   **本地測試**：在推送前，請雙擊 **`run.bat`** 確認程式可正常啟動且無錯誤。

---

## 2. 提交與上傳 (Commit & Push)
*完成特定功能或今日進度時執行*

1.  **一鍵自動上傳 (推薦)**：雙擊 **`upload_changes.bat`**。
    *   腳本會引導您輸入修改說明。
    *   自動執行 `add` -> `commit` -> `push` 完整流程。
2.  **手動上傳 (進階)**：
    ```bash
    git add .
    git commit -m "功能名稱: 簡短描述您的修改內容"
    git push origin master
    ```

---

## 3. 核心準則 (Core Rules)
*   **資料庫隔離**：請勿強制上傳 `.db` 檔案。
*   **結構對齊**：若您修改了資料庫（如 `ALTER TABLE`），必須同步更新 **`doc/schema.sql`**。
*   **告知夥伴**：完成 Push 後，請通知夥伴執行「前置作業同步」以獲取最新版。

---
*辛苦了！您的貢獻已成功同步至 GitHub 雲端。*
