@echo off
REM Optimized Launch Script for Wan 2.2 i2v on RTX 5090
REM Target: 67-80s per pass @ 832x1216, two-pass workflow
REM Created: 2025-11-23
REM Updated: Removed --force-channels-last (not compatible with video models)

echo ========================================
echo Wan 2.2 i2v - RTX 5090 Optimized Launch
echo ========================================
echo.

REM Set working directory
cd /d %~dp0..

REM ========================================
REM Environment Variable Configuration
REM ========================================

REM Disable ComfyUI Manager front-end and registry fetching (faster startup)
set DISABLE_COMFYUI_MANAGER_FRONT=1

REM Enable CUDA memory optimizations
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True

REM Disable PyTorch compile (adds VRAM overhead, causes model offloading at 81 frames)
set TORCH_COMPILE=0
set TORCH_COMPILE_MODE=reduce-overhead

REM Disable CUDA launch blocking for async execution (performance)
set CUDA_LAUNCH_BLOCKING=0

REM Optimize thread usage
set OMP_NUM_THREADS=8

REM Use lazy CUDA module loading (faster startup)
set CUDA_MODULE_LOADING=LAZY

echo Environment Variables Set:
echo   PYTORCH_CUDA_ALLOC_CONF=%PYTORCH_CUDA_ALLOC_CONF%
echo   TORCH_COMPILE=%TORCH_COMPILE%
echo   TORCH_COMPILE_MODE=%TORCH_COMPILE_MODE%
echo   OMP_NUM_THREADS=%OMP_NUM_THREADS%
echo.

REM ========================================
REM ComfyUI Launch Arguments for RTX 5090
REM ========================================

echo Starting ComfyUI with RTX 5090 optimizations...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Save environment snapshot before launch
echo Saving environment snapshot...
python scripts\save_env.py docs\env_snapshot_rtx5090.json

REM Launch ComfyUI with optimized flags
REM --normalvram: Most stable for large models, unloads models between passes
REM --reserve-vram 2: Reserve 2GB for activations (less reservation = more for models)
REM Lower reservation allows full model loading, ComfyUI will auto-unload between passes
python main.py ^
  --normalvram ^
  --reserve-vram 2 ^
  --cuda-malloc ^
  --preview-method auto ^
  --verbose INFO

REM Note: 
REM - --normalvram: Most stable option, prevents OOM at cost of some offloading on 81+ frames
REM - --reserve-vram 4: Reserves 4GB for activations
REM - --highvram and --gpu-only: Cause OOM on 81 frames (tested and failed)
REM - PyTorch attention: Auto-enabled by ComfyUI on NVIDIA + PyTorch 2.x (cannot disable)
REM - TORCH_COMPILE=0: Compile adds VRAM overhead
REM - Optimal frame counts: 25-61 frames (no offloading), 81+ frames (some offloading)
REM - For best performance: Use 61 frames (~93s, no offloading)

pause
