@echo off
REM Quick Setup Script for Frame Interpolation
REM Run this once to install dependencies

echo ======================================================================
echo ComfyUI Frame Interpolation Setup
echo ======================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at venv\
    echo Please run this from the ComfyUI root directory
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [INFO] Installing frame interpolation dependencies...
echo.

python -m pip install --quiet opencv-python watchdog tqdm

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Installation Complete!
echo ======================================================================
echo.
echo You can now use the frame interpolation scripts:
echo.
echo   1. Manual interpolation:
echo      python scripts\interpolate_video.py output\video\your-video.mp4
echo.
echo   2. Batch processing:
echo      python scripts\interpolate_video.py output\video\*.mp4 --method both
echo.
echo   3. Benchmark comparison:
echo      python scripts\benchmark_interpolation.py output\video\
echo.
echo   4. Auto-watch directory:
echo      python scripts\auto_interpolate_workflow.py --watch output\video\ --method rife
echo.
echo   5. Generate with auto-interpolation:
echo      python scripts\generate_wan22_video.py input\my-image.jpg --interpolate rife
echo.
echo See docs\FRAME_INTERPOLATION.md for full documentation
echo ======================================================================
pause




