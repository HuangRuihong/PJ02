@echo off
chcp 65001 >nul
echo [上傳] 正在執行代碼上傳精靈...

pushd "%~dp0.."
set PYTHONPATH=%CD%
python upload_changes.py
popd
pause
