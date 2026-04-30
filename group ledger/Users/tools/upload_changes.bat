@echo off
chcp 65001 >nul
echo [上傳] 正在啟動自動化提交精靈...

pushd "%~dp0"
python upload_changes.py
popd
pause
