@echo off
chcp 65001 >nul
setlocal
echo [啟動中] 正在啟動群組分帳系統 (Group Ledger)...

pushd "%~dp0.."
set PYTHONPATH=%CD%
python run.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [錯誤] 系統執行中斷或啟動失敗。
    echo 請確認已執行: pip install -r requirements.txt
    pause
)
popd
endlocal
