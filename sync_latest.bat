@echo off
chcp 65001 >nul
pushd "%~dp0"
title Split-it-Smart 🔄 同步最新進度

echo [1/3] 正在從 GitHub 獲取最新代碼 (git pull)...
git pull origin master
if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 同步失敗。請檢查您的網路連線，或是否存在未提交的衝突。
    pause
    exit /b
)

echo.
echo [2/3] 正在同步資料庫結構 (update_db)...
call update_db.bat

echo.
echo [3/3] 同步完成！
echo 現在您可以執行 run.bat 開始測試夥伴的更新了。
echo --------------------------------------------------
pause
popd
