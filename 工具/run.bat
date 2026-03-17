@echo off
rem 移動到專案根目錄 (即 c:\PJ02\mysalf)
pushd "%~dp0.."
chcp 65001 >nul
python run.py
if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 啟動 mysalf 失敗。
    echo 請確保 Python 已安裝且位在環境變數或執行 pip install -r requirements.txt。
    pause
)
popd
