@echo off
echo [Group Ledger Client] Connecting to http://127.0.0.1:8000...
cd %~dp0..
set PYTHONPATH=%CD%
python run.py --host http://127.0.0.1:8000
pause
