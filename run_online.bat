@echo off
chcp 65001 >nul
echo [啟動] Group Ledger 聯網模式...
set /p host_url="請輸入伺服器網址 (例如 https://xxxx.lvh.me): "

if "%host_url%"=="" (
    echo [資訊] 未輸入網址，將以本地模式啟動。
    python run_app.py
) else (
    echo [資訊] 正在連線至: %host_url%
    python run_app.py --host %host_url%
)

pause
