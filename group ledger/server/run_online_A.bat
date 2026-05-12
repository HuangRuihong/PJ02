@echo off
chcp 65001 >nul
cls
echo ==========================================
echo   [Server Mode] Group Ledger API Server
echo ==========================================
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set "local_ip=%%a"
    goto :found
)
:found
set "local_ip=%local_ip: =%"

echo [Info] Server IP Address : %local_ip%
echo [Info] Client should connect to : http://%local_ip%:8000
echo.
echo [Info] Starting API server on port 8000...
echo [Info] Press Ctrl+C to stop the server.
echo.
cd /d "%~dp0"
python api_server.py

pause
