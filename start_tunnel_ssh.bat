@echo off
chcp 65001 >nul
echo [隧道] 正在透過 SSH 建立公開連線網址...
echo [注意] 此視窗請勿關閉，關閉後手機將無法連線。
echo [提示] 執行後請查看下方顯示的 "tunl.ink" 或 "localhost.run" 網址。
echo.
echo ==========================================
ssh -R 80:localhost:8000 nokey@localhost.run
echo ==========================================
echo.
echo [警告] 隧道已關閉或連線中斷。
pause
