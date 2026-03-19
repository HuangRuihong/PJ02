@echo off
echo [DB Update] Checking database schema...
python "%~dp0..\backend\core\db_update.py"
if %ERRORLEVEL% equ 0 (
    echo [DB Update] Success.
) else (
    echo [DB Update] Error occurred.
)
