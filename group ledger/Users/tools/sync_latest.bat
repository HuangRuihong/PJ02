@echo off
chcp 65001 >nul
echo [拉取同步] 正在與伺服器同步程式碼...

rem 檔案在 tools/，返回專案根目錄執行 git
pushd "%~dp0..\.."
git pull origin master
if %ERRORLEVEL% neq 0 (
    echo.
    echo [錯誤] Git 同步失敗，請檢查網路或衝突。
    popd
    pause
    exit /b %ERRORLEVEL%
)
popd

echo.
echo [結構更新] 正在檢查資料庫變更...
call "%~dp0update_db.bat"

echo.
echo [完成] 資料同步作業已結束。
pause
