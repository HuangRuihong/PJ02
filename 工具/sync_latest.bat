@echo off
echo [同步] 正在從雲端同步最新代碼...

pushd "%~dp0.."
git pull origin master
if %ERRORLEVEL% neq 0 (
    echo.
    echo [錯誤] Git 同步失敗，請手動檢查網絡或衝突。
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [更新] 正在執行資料庫檢查...
call "%~dp0update_db.bat"

echo.
echo [完成] 同步與更新作業結束。
popd
pause
