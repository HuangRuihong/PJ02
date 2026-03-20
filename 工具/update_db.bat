@echo off
echo [資料庫更新] 正在檢查並應用遷移...

pushd "%~dp0.."
python backend\core\db_update.py
if %ERRORLEVEL% equ 0 (
    echo.
    echo [成功] 資料庫已是最新版本。
) else (
    echo.
    echo [錯誤] 更新資料庫時發生異常。
)
popd
