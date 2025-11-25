@echo off
REM VERIFY baseline configuration is actually loaded

echo ========================================
echo Configuration Verification
echo ========================================
echo.

cd /d %~dp0..

echo Checking launch script configuration...
echo.

echo [Environment Variables]
findstr /C:"TORCH_COMPILE" scripts\launch_wan22_rtx5090.bat
findstr /C:"DISABLE_COMFYUI_MANAGER" scripts\launch_wan22_rtx5090.bat
echo.

echo [Launch Flags]
findstr /C:"python main.py" scripts\launch_wan22_rtx5090.bat | findstr /V "REM"
echo.

echo ========================================
echo Expected Configuration:
echo ========================================
echo.
echo TORCH_COMPILE=0 (DISABLED)
echo.
echo NO --use-pytorch-cross-attention flag
echo NO --use-flash-attention flag
echo NO --use-sage-attention flag
echo.
echo Should have:
echo   --normalvram
echo   --reserve-vram 4
echo   --cuda-malloc
echo.
echo ========================================
echo.
pause

