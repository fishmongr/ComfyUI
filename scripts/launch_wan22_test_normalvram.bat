@echo off
REM Alternative VRAM mode test - normalvram instead of highvram

echo ========================================
echo Wan 2.2 i2v - Alternative VRAM Mode Test
echo ========================================
echo.

cd /d %~dp0..

set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True
set TORCH_COMPILE=0
set CUDA_LAUNCH_BLOCKING=0
set OMP_NUM_THREADS=8
set CUDA_MODULE_LOADING=LAZY

echo Testing with normalvram mode...
echo.

call venv\Scripts\activate.bat

REM Try normalvram mode instead of highvram
python main.py --normalvram --cuda-malloc

pause

