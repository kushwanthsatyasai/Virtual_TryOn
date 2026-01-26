@echo off
echo ========================================
echo VTON Pipeline - Intermediate Outputs
echo ========================================
echo.

REM Activate virtual environment
if exist venv_py311\Scripts\activate.bat (
    call venv_py311\Scripts\activate.bat
) else (
    echo Virtual environment not found!
    echo Please run this from the backend directory.
    pause
    exit /b 1
)

echo.
echo Select an option:
echo 1. Use test images from static folder
echo 2. Specify custom image paths
echo.

set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Using default test images...
    python generate_intermediate_outputs.py --person "static/test_images/person.jpg"
) else if "%choice%"=="2" (
    echo.
    set /p person_path="Enter path to person image: "
    set /p garment_path="Enter path to garment image (optional, press Enter to skip): "
    
    if "%garment_path%"=="" (
        python generate_intermediate_outputs.py --person "%person_path%"
    ) else (
        python generate_intermediate_outputs.py --person "%person_path%" --garment "%garment_path%"
    )
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Done! Check the intermediate_outputs_* folder
echo ========================================
pause
