@echo off
REM Build and install SageAttention from source for Windows
REM RTX 5090 (Blackwell architecture, compute capability 9.0)

echo ========================================
echo SageAttention Build Script for Windows
echo RTX 5090 (Blackwell - Compute 9.0)
echo ========================================
echo.

REM Activate venv
echo [1/6] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check prerequisites
echo [2/6] Checking prerequisites...
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.version.cuda}')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyTorch not found in venv
    pause
    exit /b 1
)

REM Clone SageAttention repository if not exists
echo [3/6] Checking for SageAttention repository...
if not exist "build\sageattention" (
    echo Cloning SageAttention repository...
    mkdir build 2>nul
    cd build
    git clone https://github.com/thu-ml/SageAttention.git sageattention
    cd ..
) else (
    echo SageAttention repository already exists, updating...
    cd build\sageattention
    git pull
    cd ..\..
)

REM Set environment variables for building
echo [4/6] Setting build environment...
set TORCH_CUDA_ARCH_LIST=9.0
set MAX_JOBS=8
set DISTUTILS_USE_SDK=1

REM Set CUDA_HOME to actual CUDA Toolkit (required for nvcc)
set "CUDA_HOME=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8"
echo CUDA_HOME set to: %CUDA_HOME%

REM Initialize Visual Studio Build Tools environment
echo Initializing Visual Studio Build Tools...
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64 >nul 2>&1
echo Visual Studio Build Tools initialized

REM Build and install
echo [5/6] Building SageAttention (this may take several minutes)...
echo Note: You may see warnings about CUDA architectures, this is normal
echo.
cd build\sageattention
pip install -v --no-build-isolation -e .
set BUILD_RESULT=%ERRORLEVEL%
cd ..\..

if %BUILD_RESULT% NEQ 0 (
    echo.
    echo ========================================
    echo BUILD FAILED
    echo ========================================
    echo.
    echo Common issues:
    echo 1. Missing Visual Studio Build Tools
    echo 2. CUDA Toolkit not installed
    echo 3. Incompatible PyTorch/CUDA versions
    echo.
    pause
    exit /b 1
)

REM Verify installation
echo [6/6] Verifying installation...
python -c "import sageattention; print('SageAttention installed successfully!')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: SageAttention import failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo SageAttention has been built and installed.
echo You can now enable SageAttention3 in your workflow.
echo.
pause

