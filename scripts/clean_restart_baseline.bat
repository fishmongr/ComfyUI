@echo off
REM Nuclear restart: Clear all caches and environment state

echo ========================================
echo FULL CLEAN RESTART - Baseline Test
echo ========================================
echo.

REM Kill all Python processes
echo [1/5] Killing all Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

REM Clear PyTorch cache directory
echo [2/5] Clearing PyTorch cache...
if exist "%USERPROFILE%\.cache\torch" (
    rd /s /q "%USERPROFILE%\.cache\torch" 2>nul
)

REM Clear environment variables (new shell)
echo [3/5] Starting fresh shell environment...

REM Clear ComfyUI temp directory
echo [4/5] Clearing ComfyUI temp...
if exist "temp" (
    rd /s /q "temp" 2>nul
)

echo [5/5] Starting ComfyUI with CLEAN baseline...
echo.
echo ========================================
echo VERIFY IN LOGS:
echo ========================================
echo.
echo Should NOT see:
echo   - "Using pytorch attention" (except VAE - that's OK)
echo   - "torch.compile" messages
echo   - "Compiling" messages
echo.
echo Should see:
echo   - "loaded completely" (no offloading)
echo   - Per step: ~17-18s
echo   - Run 2 should be ~120s
echo.
pause

REM Start fresh CMD to clear all environment
start cmd /k "cd /d %~dp0.. && call scripts\launch_wan22_rtx5090.bat"

echo.
echo New ComfyUI window opened with clean environment.
echo Close this window after ComfyUI starts.
pause

