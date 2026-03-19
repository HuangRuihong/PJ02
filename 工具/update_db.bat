@echo off
chcp 65001 >nul
echo [資料庫更新] 正在檢查資料庫結構...

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [錯誤] 找不到 Python 環境。請安裝 Python 以使用此工具。
    pause
    exit /b 1
)

python "%~dp0..\backend\core\db_update.py"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [資料庫更新] 成功完成。
) else (
    echo.
    echo [資料庫更新] 過程中發生錯誤，請檢查上方訊息。
)

pause
