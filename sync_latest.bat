@echo off
pushd "%~dp0"
chcp 65001 >nul

echo [1/3] Git Pulling...
git pull origin master

if %errorlevel% neq 0 (
    echo [ERROR] Pull failed.
    pause
    exit /b
)

echo [2/3] Updating Database...
call update_db.bat

echo [3/3] Done.
pause
popd
