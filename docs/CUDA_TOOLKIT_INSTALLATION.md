# CUDA Toolkit 12.8 Installation Guide

## Step 1: Download CUDA Toolkit 12.8

NVIDIA requires downloading through their official page.

### Option A: Direct Download (Recommended)
Visit this link in your browser:
```
https://developer.nvidia.com/cuda-12-8-0-download-archive
```

**Select:**
- Operating System: **Windows**
- Architecture: **x86_64**
- Version: **10** or **11** (both work)
- Installer Type: **exe (local)** ← Recommended

**Download**: `cuda_12.8.1_windows.exe` (~3.5 GB)

### Option B: Use this PowerShell command
```powershell
# Download to ComfyUI/downloads folder
Start-BitsTransfer -Source "https://developer.download.nvidia.com/compute/cuda/12.8.1/local_installers/cuda_12.8.1_windows.exe" -Destination "downloads\cuda_12.8.1_windows.exe"
```

---

## Step 2: Install CUDA Toolkit

Once downloaded, run the installer:

### Installation Options:

**1. Express Installation (Recommended)**
- Installs everything you need
- Automatically sets PATH variables
- ~6-8 minutes

**2. Custom Installation**
If you choose custom:
- ✅ **CUDA Compiler (nvcc)** - REQUIRED
- ✅ **CUDA Development** - REQUIRED  
- ✅ **CUDA Runtime** - REQUIRED
- ✅ **CUDA Documentation** - Optional
- ❌ **Driver Components** - Skip (you have 5090 drivers)
- ❌ **Visual Studio Integration** - Optional

**Installation Path:**
Default: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8`

---

## Step 3: Verify Installation

After installation, **OPEN A NEW TERMINAL** and verify:

```batch
# Check nvcc compiler
nvcc --version

# Should show:
# Cuda compilation tools, release 12.8, V12.8.xxx
```

```batch
# Check CUDA_HOME
echo %CUDA_HOME%

# Should show:
# C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8
```

If `CUDA_HOME` is not set:
```batch
setx CUDA_HOME "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8"
```

---

## Step 4: Install Visual Studio Build Tools (if needed)

Check if you have C++ compiler:
```batch
where cl
```

If not found, download Build Tools:
1. Visit: https://visualstudio.microsoft.com/downloads/
2. Scroll to "Tools for Visual Studio"
3. Download "Build Tools for Visual Studio 2022"
4. Install with:
   - ✅ "Desktop development with C++"
   - ✅ MSVC v143 build tools
   - ✅ Windows 10/11 SDK

---

## Step 5: Build SageAttention

After installation and verification, **OPEN A NEW TERMINAL** in ComfyUI directory and run:

```batch
.\scripts\build_sageattention.bat
```

This will:
1. Activate venv
2. Check prerequisites
3. Clone SageAttention repo (if needed)
4. Build with CUDA 12.8
5. Install into your venv
6. Verify installation

**Build time**: 5-10 minutes

---

## Troubleshooting

### Issue: "nvcc not found"
**Solution**: Open a NEW terminal after installation (to refresh PATH)

### Issue: "CUDA_HOME not set"
**Solution**:
```batch
setx CUDA_HOME "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8"
# Then open new terminal
```

### Issue: "cl.exe not found"
**Solution**: Install Visual Studio Build Tools (Step 4)

### Issue: Build fails with "compute capability" error
**Solution**: Already set to 9.0 (Blackwell) in build script

---

## After Successful Build

Once SageAttention is built:

1. **Test a quick generation**:
```batch
python scripts/generate_wan22_video.py input/sogni-photobooth-my-polar-bear-baby-raw.jpg --frames 25 --settings "4step_sage3"
```

2. **Enable SageAttention3 in workflow**:
```batch
python scripts/enable_sageattention.py
```

3. **Run benchmarks**:
```batch
python scripts/wan22_benchmark.py --test-frames 25,49,81 --settings "4step_sage3" --output benchmarks/rtx5090_sage3.csv
```

---

## Current Status

- ✅ Build script created: `scripts/build_sageattention.bat`
- ⏳ **Next**: Download CUDA Toolkit 12.8
- ⏳ **Then**: Install CUDA Toolkit
- ⏳ **Then**: Build SageAttention
- ⏳ **Finally**: Benchmark with SageAttention3 enabled

---

## Let Me Know When Ready!

Once you've:
1. ✅ Downloaded CUDA Toolkit
2. ✅ Installed it
3. ✅ Verified `nvcc --version` works in a NEW terminal

Just say "ready" and I'll run the build script!

