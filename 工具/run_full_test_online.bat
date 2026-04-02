@echo off
echo ==========================================
echo    Group Ledger [Online Mode] Diagnostics
echo ==========================================
echo [1/2] Connecting to Server http://127.0.0.1:8000...
cd %~dp0..
set PYTHONPATH=%CD%
python tests/online_diagnostic_suite.py
echo.
echo ==========================================
echo    Diagnostics Complete.
echo ==========================================
pause
