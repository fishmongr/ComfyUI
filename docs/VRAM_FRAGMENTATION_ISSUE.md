# VRAM Fragmentation Issue

## Problem

After multiple generations in a single ComfyUI session, VRAM fragments and models are forced to offload, causing ~40% performance degradation.

## Evidence

**Fresh Start (Good):**
```
loaded completely; 14971.79 MB usable, 13629.08 MB loaded, full load: True
100%|████| 2/2 [00:34<00:00, 17.38s/it]
Prompt executed in 93.44 seconds
```

**After Multiple Runs (Degraded):**
```
loaded partially; 11332.26 MB usable, 11332.26 MB loaded, 2296.82 MB offloaded
100%|████| 2/2 [01:05<00:00, 32.80s/it]
Prompt executed in 160.31 seconds
```

**Performance Impact:**
- Fresh: 93.44s (optimal)
- Fragmented: 160.31s (71% slower!)
- Cause: Model offloading due to fragmentation

## Root Cause

CUDA memory fragmentation occurs when:
1. Multiple generations run in sequence
2. Models load/unload repeatedly
3. VRAM becomes fragmented (unusable gaps)
4. Even with 32GB total, can't allocate contiguous 13.6GB for model
5. System falls back to partial loading + offloading

## Solutions

### Solution 1: Restart ComfyUI Periodically (RECOMMENDED)

**When:**
- After every 5-10 generations
- When you notice performance degradation
- When logs show "loaded partially"

**How:**
```batch
# Close ComfyUI (Ctrl+C)
# Restart:
.\scripts\launch_wan22_rtx5090.bat
```

**Result:**
- Clears all fragmentation
- Returns to optimal performance
- Simple and reliable

### Solution 2: Monitor and Alert

**Create a monitoring script to watch for offloading:**

```python
# In generation script, check logs for:
if "loaded partially" in log:
    print("WARNING: Models offloading, restart recommended")
    print("Performance degraded by ~70%")
```

### Solution 3: Increase PYTORCH_CUDA_ALLOC_CONF

**Try more aggressive memory management:**

```batch
set PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256,expandable_segments:True,garbage_collection_threshold:0.8
```

**This may help but not guaranteed.**

### Solution 4: Clear Cache Between Generations

**Add to workflow/script:**

```python
import torch
import gc

# After each generation:
torch.cuda.empty_cache()
gc.collect()
```

**Note:** This may help but doesn't fully prevent fragmentation.

## Recommended Workflow

### For Single Videos:
1. Start ComfyUI
2. Generate video
3. Close ComfyUI when done
4. No fragmentation issues

### For Batch Processing:
1. Start ComfyUI
2. Generate 5-10 videos
3. **Restart ComfyUI** (prevent fragmentation)
4. Repeat

### For Long-Running Sessions:
1. Monitor logs for "loaded partially"
2. When seen, restart ComfyUI
3. Continue batch processing

## Detection

**Watch for these signs:**
- ✅ "loaded completely" = Good (optimal performance)
- ⚠️ "loaded partially" = Bad (restart needed)
- ⚠️ "offloaded" in logs = Bad (restart needed)
- ⚠️ Per-step time > 20s = Bad (was ~17s optimal)

## Performance Comparison

| State | Load Status | Per Step | Total (81f) | Action |
|-------|-------------|----------|-------------|--------|
| **Optimal** | loaded completely | 17.4s | 93-120s | ✅ Good |
| **Fragmented** | loaded partially | 32.8s | 160s+ | ⚠️ Restart |

## Long-term Solution (Advanced)

**Use separate ComfyUI instances for batch processing:**

```python
# Launch new ComfyUI for each batch of 5-10 videos
# Prevents fragmentation accumulation
# More complex but fully automated
```

## Summary

**The Issue:** VRAM fragmentation after multiple runs  
**The Symptom:** "loaded partially" and 70% slower performance  
**The Fix:** Restart ComfyUI periodically  
**The Prevention:** Restart after 5-10 generations  

Your baseline config is optimal - the degradation is purely from fragmentation, not configuration issues.

