@echo off
REM Optimized Launch Script for Wan 2.2 i2v on A100
REM Target: 75-95s per pass @ 832x1216, two-pass workflow
REM Updated: Removed --force-channels-last (not compatible with video models)

echo ========================================
echo Wan 2.2 i2v - A100 Optimized Launch
echo ========================================
echo.

REM Set working directory
cd /d %~dp0..

REM ========================================
REM Environment Variable Configuration
REM ========================================

REM Enable CUDA memory optimizations (generous for 40/80GB)
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True

REM Enable PyTorch compile
set TORCH_COMPILE=1
set TORCH_COMPILE_MODE=max-autotune

REM Disable CUDA launch blocking
set CUDA_LAUNCH_BLOCKING=0

REM Optimize thread usage for data center
set OMP_NUM_THREADS=16

REM Use lazy CUDA module loading
set CUDA_MODULE_LOADING=LAZY

echo Environment Variables Set:
echo   PYTORCH_CUDA_ALLOC_CONF=%PYTORCH_CUDA_ALLOC_CONF%
echo   TORCH_COMPILE=%TORCH_COMPILE%
echo   OMP_NUM_THREADS=%OMP_NUM_THREADS%
echo.

REM ========================================
REM ComfyUI Launch Arguments for A100
REM ========================================

echo Starting ComfyUI with A100 optimizations...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Save environment snapshot
python scripts\save_env.py docs\env_snapshot_a100.json

REM Launch ComfyUI with optimized flags for A100 (Ampere architecture)
python main.py ^
  --gpu-only ^
  --cuda-malloc ^
  --preview-method auto ^
  --verbose INFO

REM Note:
REM - gpu-only for maximum speed (40/80GB VRAM is plenty)
REM - Removed --force-channels-last (not compatible with video models)
REM - Use FlashAttention via launch flag if needed: --use-flash-attention

pause
