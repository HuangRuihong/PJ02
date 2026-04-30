@echo off
chcp 65001 >nul
echo [資料庫更新] 正在檢查結構...

pushd "%~dp0"
python db_update.py
if %ERRORLEVEL% equ 0 (
    echo.
    echo [成功] 資料庫已是最新狀態。
) else (
    echo.
    echo [錯誤] 更新時發生異常。
)
popd
pause
