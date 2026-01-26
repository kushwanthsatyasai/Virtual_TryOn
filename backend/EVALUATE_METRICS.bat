@echo off
echo ================================================
echo Virtual Try-On Quality Evaluation
echo ================================================
echo.

REM Activate virtual environment
call venv_py311\Scripts\activate.bat

REM Check if images exist
if not exist "test_images\test_user.png" (
    echo Error: test_user.png not found!
    pause
    exit /b 1
)

if not exist "test_images\test_cloth.png" (
    echo Error: test_cloth.png not found!
    pause
    exit /b 1
)

REM You need a generated output to evaluate
REM Replace this with your actual generated try-on image path
set GENERATED_IMAGE=static\generated_outputs\tryon_result.png

if not exist "%GENERATED_IMAGE%" (
    echo.
    echo Note: No generated image found at %GENERATED_IMAGE%
    echo Please run a virtual try-on first, or specify a different image.
    echo.
    echo Usage: python evaluate_tryon_quality.py --generated [path] --person [path] --cloth [path]
    echo.
    pause
    exit /b 1
)

echo Running comprehensive quality evaluation...
echo.

python evaluate_tryon_quality.py ^
    --generated "%GENERATED_IMAGE%" ^
    --person "test_images\test_user.png" ^
    --cloth "test_images\test_cloth.png" ^
    --output "evaluation_metrics.json"

echo.
echo ================================================
echo Evaluation complete! Check evaluation_metrics.json
echo ================================================
pause
