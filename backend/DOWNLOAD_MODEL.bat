@echo off
echo Downloading Virtual Try-On Model...
echo.

cd /d %~dp0
call venv_py311\Scripts\activate.bat

python download_vto_model.py

pause

