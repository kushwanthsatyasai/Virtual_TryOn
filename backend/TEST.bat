@echo off
echo Testing Virtual Try-On with sample images...
echo.

cd /d %~dp0
call venv_py311\Scripts\activate.bat

python run_with_real_images.py

pause

