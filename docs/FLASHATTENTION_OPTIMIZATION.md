# FlashAttention Optimization - RTX 5090

## Overview

Successfully enabled **PyTorch SDPA (Scaled Dot Product Attention) with FlashAttention backend** for optimal attention mechanism performance on RTX 5090.

## Implementation

### What is PyTorch SDPA?

PyTorch 2.0+ includes `torch.nn.functional.scaled_dot_product_attention` (SDPA) which automatically selects the fastest attention backend available:

1. **FlashAttention** (CUDA kernels) - Fastest, most memory efficient
2. **Memory-Efficient Attention** (xformers) - Good fallback
3. **Math SDPA** (PyTorch native) - Compatibility fallback

### Why This is Best for RTX 5090

- ✅ **No external dependencies** - Built into PyTorch 2.10
- ✅ **All backends enabled** - Automatically uses FlashAttention where applicable
- ✅ **Most stable** - No compilation required
- ✅ **Blackwell optimized** - PyTorch CUDA kernels are optimized for latest architectures
- ✅ **Zero overhead** - No custom node or external library needed

### Alternative: FlashAttention-2/3 (Not Recommended for Windows)

**FlashAttention-2:**
- Requires compilation from source on Windows
- Can be challenging to build with MSVC
- Minimal performance benefit over PyTorch SDPA on RTX 5090

**FlashAttention-3:**
- Optimized for H100 (Hopper) architecture, not RTX 5090 (Blackwell)
- Requires PyTorch 2.8.0+ (nightly has compilation issues)
- Pre-built wheels not widely available for Windows
- FP8 optimizations (FA3's main benefit) not yet utilized by Wan 2.2 models

## Configuration

### Launch Script Changes

**File:** `scripts/launch_wan22_rtx5090.bat`

**Added:**
```batch
--use-pytorch-cross-attention
```

**What it does:**
- Instructs ComfyUI to use PyTorch's native SDPA
- PyTorch automatically selects FlashAttention backend when available
- Falls back to mem-efficient or math SDPA if needed

### Verification

**Check SDPA backends enabled:**
```python
import torch
print('flash_sdp:', torch.backends.cuda.flash_sdp_enabled())      # True
print('mem_efficient_sdp:', torch.backends.cuda.mem_efficient_sdp_enabled())  # True
print('math_sdp:', torch.backends.cuda.math_sdp_enabled())       # True
```

**Check PyTorch SDPA is available:**
```python
import torch.nn.functional as F
print('SDPA available:', hasattr(F, 'scaled_dot_product_attention'))  # True
```

## Expected Performance Impact

### Baseline (Sub-Quadratic Attention)
- ComfyUI default: `attention_sub_quad`
- 81 frames @ 832x1216: **~75s** per pass

### With PyTorch SDPA + FlashAttention
- Expected: `attention_pytorch` (using FlashAttention backend)
- 81 frames @ 832x1216: **~60-70s** per pass (est. 10-20% speedup)
- Lower VRAM usage for attention operations
- More consistent performance (less dependent on sequence length)

**Note:** Actual gains depend on:
- Attention layer count in Wan 2.2 models
- Sequence length (longer sequences = bigger gains)
- Other bottlenecks (VAE, LoRA, etc.)

## Benchmarking Plan

### Test 1: Direct Comparison
**Baseline (no flag):**
```batch
python scripts\generate_wan22_video.py input\sogni-photobooth-my-polar-bear-baby-raw.jpg --frames 25 --settings "4step_25f_baseline"
```

**With PyTorch SDPA:**
```batch
REM Launch with updated launch_wan22_rtx5090.bat
python scripts\generate_wan22_video.py input\sogni-photobooth-my-polar-bear-baby-raw.jpg --frames 25 --settings "4step_25f_flash"
```

### Test 2: Full Benchmark Suite
```batch
python scripts\wan22_benchmark.py --test-frames 25,49,81 --settings "4step_flash" --output benchmarks\rtx5090_flashattn.csv
```

Compare against: `benchmarks\rtx5090_baseline.csv`

## ComfyUI Log Verification

When launching ComfyUI, you should see:
```
Using pytorch attention
```

Instead of:
```
Using sub quadratic optimization for attention
```

## Alternative Attention Options

If PyTorch SDPA doesn't provide expected gains:

### Option 1: xformers
```batch
pip install xformers
REM Remove --use-pytorch-cross-attention from launch script
REM Will use xformers by default if installed
```

### Option 2: Sage Attention (if build succeeds)
```batch
REM Requires building from source (currently blocked by PyTorch nightly bug)
--use-sage-attention
```

### Option 3: Split Attention (Fallback for low VRAM)
```batch
--use-split-cross-attention
REM Less efficient but more memory-friendly
```

## Next Steps

1. ✅ **Test current setup** - Run benchmark with PyTorch SDPA
2. ⏳ **Compare results** - Check if 10-20% speedup achieved
3. ⏳ **Proceed to Frame Interpolation** - Bigger performance win (16fps → 32fps)
4. ⏳ **Revisit SageAttention** - When PyTorch stable version is compatible

## Summary

**Current Status:** ✅ PyTorch SDPA with FlashAttention backend enabled

**Expected Performance:** 
- Generation: 60-70s per pass (down from 75s)
- VRAM: Similar or slightly better
- Stability: Excellent (built-in, no custom compilation)

**Next Optimization Priority:** Frame Interpolation (RIFE/FILM) for 16fps → 32fps

