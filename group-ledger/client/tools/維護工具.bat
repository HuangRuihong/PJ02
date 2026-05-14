@echo off
chcp 65001 >nul
cd /d "%~dp0"
python maintenance_tool.py
pause
