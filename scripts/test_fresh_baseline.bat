@echo off
REM Test script: Fresh restart and single generation to verify baseline performance

echo ========================================
echo Fresh Baseline Performance Test
echo ========================================
echo.
echo This script will:
echo   1. Kill any running ComfyUI instances
echo   2. Start ComfyUI fresh
echo   3. Wait for you to run ONE 81-frame test
echo.

REM Kill existing ComfyUI processes
echo Killing existing ComfyUI processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *ComfyUI*" 2>nul
timeout /t 2 >nul

echo.
echo Starting fresh ComfyUI instance...
echo.
echo ========================================
echo IMPORTANT:
echo ========================================
echo.
echo After ComfyUI starts:
echo   1. Generate ONE 81-frame video
echo   2. Note the time from logs
echo   3. Check for "loaded completely" vs "loaded partially"
echo.
echo Expected with fresh restart:
echo   - "loaded completely" (no offloading)
echo   - Time: ~120s (matching your baseline)
echo   - Per step: ~17-18s
echo.
echo If you see "loaded partially":
echo   - Models are offloading
echo   - Performance will be degraded (~160s)
echo   - Something else is using VRAM
echo.
pause

REM Launch with baseline config
call scripts\launch_wan22_rtx5090.bat

