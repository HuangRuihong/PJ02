@echo off
pushd "%~dp0"
python run.py
if %errorlevel% neq 0 (
    echo.
    echo [Error] Failed to start run.py
    echo Please make sure Python is installed and in your PATH.
    pause
)
popd
