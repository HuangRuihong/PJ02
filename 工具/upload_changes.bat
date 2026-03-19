@echo off
chcp 65001 >nul
pushd "%~dp0"
python ..\upload_changes.py
popd
