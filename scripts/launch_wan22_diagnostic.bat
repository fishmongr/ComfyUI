@echo off
REM Diagnostic Launch Script - Test without torch.compile
REM Use this to isolate the OOM issue

echo ========================================
echo Wan 2.2 i2v - RTX 5090 DIAGNOSTIC Launch
echo ========================================
echo.
echo Testing WITHOUT torch.compile to diagnose OOM
echo.

REM Set working directory
cd /d %~dp0..

REM ========================================
REM Environment Variable Configuration
REM ========================================

REM Enable CUDA memory optimizations
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True

REM DISABLE torch.compile for testing
set TORCH_COMPILE=0

REM Disable CUDA launch blocking
set CUDA_LAUNCH_BLOCKING=0

REM Optimize thread usage
set OMP_NUM_THREADS=8

REM Use lazy CUDA module loading
set CUDA_MODULE_LOADING=LAZY

echo Environment Variables Set:
echo   PYTORCH_CUDA_ALLOC_CONF=%PYTORCH_CUDA_ALLOC_CONF%
echo   TORCH_COMPILE=%TORCH_COMPILE% (DISABLED for testing)
echo   OMP_NUM_THREADS=%OMP_NUM_THREADS%
echo.

REM ========================================
REM ComfyUI Launch Arguments
REM ========================================

echo Starting ComfyUI in diagnostic mode...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Launch with minimal flags
python main.py ^
  --highvram ^
  --cuda-malloc

echo.
echo If this works, the issue was torch.compile
echo If this still OOMs, try disabling SageAttention3 in workflow
echo.

pause

