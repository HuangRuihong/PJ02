@echo off
chcp 65001 >nul
cls
echo ==========================================
echo   [Client Mode] Group Ledger Starting...
echo ==========================================
echo.
set /p host_url="Please enter Server URL (e.g., https://[IP_ADDRESS]:8000): "

if "%host_url%"=="" (
    echo.
    echo [Info] No URL entered, starting in Local Mode...
    python run_app.py
) else (
    echo.
    echo [Info] Connecting to: "%host_url%"
    python run_app.py --host "%host_url%"
)

pause
