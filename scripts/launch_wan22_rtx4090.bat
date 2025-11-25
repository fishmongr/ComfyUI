@echo off
REM Optimized Launch Script for Wan 2.2 i2v on RTX 4090
REM Target: 80-100s per pass @ 832x1216, two-pass workflow
REM Updated: Removed --force-channels-last (not compatible with video models)

echo ========================================
echo Wan 2.2 i2v - RTX 4090 Optimized Launch
echo ========================================
echo.

REM Set working directory
cd /d %~dp0..

REM ========================================
REM Environment Variable Configuration
REM ========================================

REM Enable CUDA memory optimizations (more conservative for 24GB)
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256,expandable_segments:True

REM Enable PyTorch compile
set TORCH_COMPILE=1
set TORCH_COMPILE_MODE=max-autotune

REM Disable CUDA launch blocking for async execution
set CUDA_LAUNCH_BLOCKING=0

REM Optimize thread usage
set OMP_NUM_THREADS=8

REM Use lazy CUDA module loading
set CUDA_MODULE_LOADING=LAZY

echo Environment Variables Set:
echo   PYTORCH_CUDA_ALLOC_CONF=%PYTORCH_CUDA_ALLOC_CONF%
echo   TORCH_COMPILE=%TORCH_COMPILE%
echo   OMP_NUM_THREADS=%OMP_NUM_THREADS%
echo.

REM ========================================
REM ComfyUI Launch Arguments for RTX 4090
REM ========================================

echo Starting ComfyUI with RTX 4090 optimizations...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Save environment snapshot before launch
python scripts\save_env.py docs\env_snapshot_rtx4090.json

REM Launch ComfyUI with optimized flags for 24GB VRAM
python main.py ^
  --normalvram ^
  --reserve-vram 4 ^
  --cuda-malloc ^
  --preview-method auto ^
  --verbose INFO

REM Note: 
REM - normalvram instead of highvram (24GB needs careful management)
REM - reserve-vram 4 to prevent OOM on two-pass workflows
REM - Removed --force-channels-last (not compatible with video models)

pause
