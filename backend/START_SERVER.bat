@echo off
REM Start the Complete API Server
REM ==============================

cd /d %~dp0
echo.
echo ================================================
echo   Starting Virtue Try-On Complete API
echo ================================================
echo.

REM Activate virtual environment
call venv_py311\Scripts\activate.bat

REM Start server
python start_server_clean.py

pause
