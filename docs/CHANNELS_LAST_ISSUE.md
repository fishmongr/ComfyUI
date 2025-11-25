# Channels-Last Format Issue

## Problem

The `--force-channels-last` flag causes an error with Wan 2.2 video models:

```
RuntimeError: required rank 4 tensor to use channels_last format
```

## Explanation

**Channels-last format** is a memory layout optimization for **4D tensors**:
- 4D tensor: `(batch, channels, height, width)`
- Channels-last: `(batch, height, width, channels)`

**Video models use 5D tensors**:
- 5D tensor: `(batch, channels, time/frames, height, width)`
- No channels-last format for 5D tensors in PyTorch

## Impact

**Removed from all launch scripts:**
- `--force-channels-last` flag removed
- Not applicable to video diffusion models
- Only works with image models (2D convolutions)

## What This Means

- **No performance loss**: This optimization doesn't apply to video models anyway
- **Fixed scripts**: All three GPU launch scripts updated
- **Still optimized**: Other optimizations remain (TORCH_COMPILE, CUDA allocator, etc.)

## Updated Launch Scripts

All scripts have been corrected:
- ✅ `scripts/launch_wan22_rtx5090.bat`
- ✅ `scripts/launch_wan22_rtx4090.bat`
- ✅ `scripts/launch_wan22_a100.bat`

## Remaining Optimizations

Your launch script still includes:
- ✅ `TORCH_COMPILE=1` (was disabled, now enabled)
- ✅ Optimized CUDA memory allocator
- ✅ `--highvram` (keeps models in VRAM)
- ✅ `--cuda-malloc` (async CUDA memory allocation)
- ✅ Thread optimization (OMP_NUM_THREADS)
- ✅ Lazy CUDA module loading

## Next Steps

**Restart ComfyUI:**

```batch
cd C:\Users\markl\Documents\git\ComfyUI
.\scripts\launch_wan22_rtx5090.bat
```

This should now start without errors. Your workflow already has SageAttention3 enabled, so all optimizations are in place.

