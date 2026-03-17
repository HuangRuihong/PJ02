@echo off
pushd "%~dp0"
chcp 65001 >nul

echo [1/3] 正在從 Git 拉取更新...
git pull origin master

if %errorlevel% neq 0 (
    echo [錯誤] 拉取失敗。
    pause
    exit /b
)

echo [2/3] 正在更新資料庫...
call update_db.bat

echo [3/3] 完成。
pause
popd
