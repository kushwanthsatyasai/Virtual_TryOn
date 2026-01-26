@echo off
cd /d "%~dp0"
echo.
echo ===============================================
echo    Kolors Model Downloader
echo ===============================================
echo.
echo Starting download...
echo.
call venv_py311\Scripts\python.exe download_kolors_model.py
echo.
pause

