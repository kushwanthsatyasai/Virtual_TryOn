@echo off
echo Starting Virtual Try-On Backend...
echo.

cd /d %~dp0
call venv_py311\Scripts\activate.bat

echo Running FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

