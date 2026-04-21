@echo off
chcp 65001 >nul
echo [伺服器] 正在啟動 Group Ledger 行動端同步伺服器...
echo [資訊] 請確保手機與電腦連在同一個 Wi-Fi 網域。
echo [網址] 外部連線請先啟動 start_tunnel_ssh.bat。
echo.

cd /d "%~dp0"
python server/api_server.py

pause
