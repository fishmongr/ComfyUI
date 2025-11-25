# Building SageAttention on Windows - Requirements

## Current Issue

SageAttention build is failing because it needs **nvcc** (NVIDIA CUDA Compiler), which is not included in PyTorch's bundled CUDA libraries.

## What You Need to Install

### 1. CUDA Toolkit 12.8 (matches your PyTorch CUDA version)

**Download:**
- https://developer.nvidia.com/cuda-12-8-0-download-archive
- Select: Windows → x86_64 → 10/11 → exe (local)
- Size: ~3.5 GB

**What to install:**
- ✅ CUDA Compiler (nvcc) - **REQUIRED**
- ✅ CUDA Development Tools
- ✅ CUDA Runtime
- ❌ Driver (you already have RTX 5090 drivers)
- ❌ Visual Studio Integration (optional)

### 2. Visual Studio Build Tools (if not installed)

**Download:**
- https://visualstudio.microsoft.com/downloads/
- Scroll down to "Tools for Visual Studio"
- Download "Build Tools for Visual Studio 2022"

**What to install:**
- ✅ "Desktop development with C++"
- ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
- ✅ Windows 10/11 SDK

---

## After Installing CUDA Toolkit

### Step 1: Verify CUDA Installation

```batch
# Open a NEW terminal (to get updated PATH)
nvcc --version
```

Should show: `Cuda compilation tools, release 12.8`

### Step 2: Set CUDA_HOME Environment Variable

The installer should set this automatically, but verify:

```batch
echo %CUDA_HOME%
```

Should show: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8`

If not set:
```batch
setx CUDA_HOME "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8"
```

### Step 3: Run the Build Script

```batch
.\scripts\build_sageattention.bat
```

---

## Alternative: Skip SageAttention for Now

**Your current performance is EXCELLENT without SageAttention:**
- ✅ 80.9s per pass for 81 frames (5s videos)
- ✅ Within 1% of target (67-80s range)
- ✅ Production ready
- ✅ Linear scaling

**SageAttention would provide:**
- 🎁 10-20% speed boost (bonus, not critical)
- 🎁 Better memory efficiency
- 🎁 Potential fix for 161-frame slowdown

**Recommendation:**
1. **Option A**: Proceed without SageAttention → Frame Interpolation (Phase 2)
2. **Option B**: Install CUDA Toolkit → Build SageAttention → Benchmark

---

## Why Full CUDA Toolkit is Needed

PyTorch bundles CUDA **runtime libraries** (`.dll` files) for running code, but not the **development tools** needed for building:

| Component | PyTorch Bundled | Full CUDA Toolkit |
|-----------|-----------------|-------------------|
| CUDA Runtime (cudart) | ✅ Yes | ✅ Yes |
| cuDNN, cuBLAS, etc. | ✅ Yes | ✅ Yes |
| **nvcc Compiler** | ❌ No | ✅ **Yes** |
| CUDA Headers | ❌ No | ✅ **Yes** |
| Development Libraries | ❌ No | ✅ **Yes** |

**Size comparison:**
- PyTorch CUDA libraries: ~500 MB
- Full CUDA Toolkit: ~3.5 GB

---

## Estimated Time

- **CUDA Toolkit download**: 5-10 minutes (3.5 GB)
- **CUDA Toolkit install**: 5-10 minutes
- **Visual Studio Build Tools** (if needed): 10-15 minutes
- **SageAttention build**: 5-10 minutes
- **Total**: 30-45 minutes

---

## Decision Point

**What would you like to do?**

### A. Install CUDA Toolkit and build SageAttention
- **Pro**: Potential 10-20% speed improvement
- **Con**: 30-45 minutes setup time
- **Risk**: Build may still fail with other issues

### B. Proceed without SageAttention
- **Pro**: Already at excellent performance
- **Pro**: Can continue to Frame Interpolation immediately
- **Con**: Miss out on potential 10-20% optimization

---

## My Recommendation

**Proceed to Frame Interpolation (Option B)** because:

1. **Current performance is excellent** (80.9s per pass vs 67-80s target)
2. **Frame interpolation is critical** for final 32fps delivery
3. **SageAttention can be added later** if needed
4. **Minimize risk** of getting stuck on build issues

You can always come back and install CUDA Toolkit + build SageAttention later if you need that extra 10-20% speed boost.

---

## If You Choose to Install CUDA Toolkit

Let me know once you've:
1. ✅ Downloaded CUDA Toolkit 12.8
2. ✅ Installed it (with nvcc compiler)
3. ✅ Verified `nvcc --version` works
4. ✅ Opened a new terminal

Then I'll run the build script again and it should work!


