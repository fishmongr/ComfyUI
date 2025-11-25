# OOM Error Troubleshooting

## Issue

Getting OOM (Out of Memory) error on RTX 5090 (32GB VRAM) during generation:

```
torch.OutOfMemoryError: Allocation on device
```

This is unexpected with 32GB VRAM for 832x1216, 49 frames.

## Likely Causes

### 1. TORCH_COMPILE Initial Compilation
**Most Likely**: `TORCH_COMPILE=1` causes PyTorch to compile the model on first run, which requires significant extra VRAM for:
- Graph tracing
- Kernel compilation
- Optimization passes

**Solution**: Disable torch.compile for first run, then re-enable after warm-up.

### 2. SageAttention3 Compatibility
The SageAttention3 nodes in your workflow might have issues with:
- Wan 2.2 video models
- PyTorch 2.10 dev version
- RTX 5090 Blackwell architecture (very new)

**Solution**: Temporarily disable SageAttention3 nodes in workflow.

### 3. Memory Fragmentation
Multiple model loads (high noise + low noise + VAE + text encoder) might fragment VRAM.

**Solution**: Use model unloading between passes.

## Troubleshooting Steps

### Step 1: Test Without TORCH_COMPILE

```batch
cd C:\Users\markl\Documents\git\ComfyUI
.\scripts\launch_wan22_diagnostic.bat
```

This launches with `TORCH_COMPILE=0`. If this works:
- **First generation will be slower** (no compilation)
- **Subsequent generations normal speed**
- **Can re-enable torch.compile after warm-up**

### Step 2: Disable SageAttention3 in Workflow

If diagnostic mode still OOMs:

1. Open your workflow in ComfyUI
2. Find nodes 117 and 118 (`Sage3AttentionOnlySwitch`)
3. Set `enable=false` on both
4. Run generation

This will use PyTorch native attention instead.

### Step 3: Reduce Initial Frame Count

If still OOMing, test with fewer frames:
- Change `length` from 49 to 25 (about 1.5s)
- Verify generation works
- Gradually increase frame count

### Step 4: Check VRAM Usage

Monitor VRAM during generation:

```batch
# In another terminal
nvidia-smi dmon -s um -d 1
```

Watch memory usage. With 32GB, you should have plenty of headroom.

## Expected VRAM Usage

Based on your workflow notes for RTX 4090 (24GB):
- fp8_scaled + 4step LoRA @ 640x640: 83% of 24GB ≈ 20GB

For RTX 5090 @ 832x1216 (higher resolution):
- Estimated: 22-25GB
- Should fit comfortably in 32GB

## Recommended Fix

**Use diagnostic launch script first:**

```batch
.\scripts\launch_wan22_diagnostic.bat
```

**Once working:**
1. First run will be slower (no torch.compile)
2. Models will be cached/optimized
3. Subsequent runs should be faster
4. Can re-enable torch.compile later after warm-up

**Then test with full optimizations:**

```batch
.\scripts\launch_wan22_rtx5090.bat
```

## If Problem Persists

The issue might be:
1. **Workflow settings**: Frame count too high for first pass
2. **Model loading**: Need to unload between passes
3. **SageAttention3**: Compatibility issue with RTX 5090/PyTorch 2.10
4. **CUDA/PyTorch bug**: Dev version instability

**Workaround**: Use diagnostic script (TORCH_COMPILE=0) for production until issue is resolved.

## Performance Impact

**Without torch.compile:**
- First generation: Same speed (no compilation overhead)
- Subsequent: 5-15% slower than with torch.compile
- Still should hit 67-80s per pass target

**Without SageAttention3:**
- 10-20% slower than with SageAttention3
- Still faster than without 4-step LoRA
- More stable/compatible

## Action Plan

1. ✅ Use diagnostic launch script
2. ✅ Test generation (should work)
3. ✅ Time it (looking for 67-80s per pass)
4. ⏳ If good performance, keep TORCH_COMPILE=0 for now
5. ⏳ Install frame interpolation next
6. ⏳ Revisit torch.compile optimization later

