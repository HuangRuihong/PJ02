@echo off
echo [Group Ledger Server] Starting... (Central Sync Center)
cd %~dp0..
set PYTHONPATH=%CD%
python backend/server/app.py
pause
