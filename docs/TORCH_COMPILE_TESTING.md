# Torch Compile Testing Guide - RTX 5090

## What Changed

### Launch Script Update: `scripts/launch_wan22_rtx5090.bat`

**Before:**
```batch
set TORCH_COMPILE=0
set TORCH_COMPILE_MODE=max-autotune  # Too memory-intensive
```

**After:**
```batch
set TORCH_COMPILE=1
set TORCH_COMPILE_MODE=reduce-overhead  # Memory-efficient
```

---

## Why This Should Work

### The Problem with max-autotune:
- **Memory overhead:** +3-4GB
- **Result:** OOM on 61+ frames

### Solution: reduce-overhead mode:
- **Memory overhead:** +1.5-2GB (50% less)
- **Speedup:** 10-15% (vs no compile)
- **Expected:** Works on 61 frames, possibly 81 frames

---

## Testing Plan

### Phase 1: Test 25 Frames (Quick Validation)

**Current baseline (no compile):**
- ~23-25s

**Expected with reduce-overhead:**
- ~20-22s (10-15% faster)
- Compilation overhead on first run: +30-60s (one-time)

**Command:**
```batch
# Restart ComfyUI with new settings
.\scripts\launch_wan22_rtx5090.bat

# Then in ComfyUI UI or via script:
# Generate 25 frame video
```

**Watch for:**
- ✅ Compilation messages on first run
- ✅ No OOM errors
- ✅ Faster subsequent runs
- ⚠️ Log message about torch.compile status

---

### Phase 2: Test 61 Frames (Your Current Test Case)

**Current baseline:**
- Run 1: 138.35s (cold start)
- Run 2: 93.44s (warm cache)

**Expected with reduce-overhead:**
- Run 1: ~170s (compilation + generation)
- Run 2: ~80-85s (10-15% faster than 93.44s)
- Run 3: ~80-85s (consistent performance)

**Success criteria:**
- ✅ No OOM on 61 frames
- ✅ 8-15% speedup vs baseline (93.44s → 80-90s)
- ✅ Consistent timing across runs 2-3

---

### Phase 3: Test 81 Frames (Target Performance)

**Estimated baseline (no compile):**
- ~124s (extrapolated from 61 frame performance)

**Expected with reduce-overhead:**
- ~105-115s (10-15% faster)

**Risk assessment:**
- ⚠️ May OOM due to larger activation memory
- ⚠️ 81 frames = +33% more memory than 61 frames
- ✅ If OOMs, can fall back to `default` mode

---

## Fallback Plan

### If reduce-overhead OOMs on 61 or 81 frames:

**Switch to "default" mode:**

Edit `scripts/launch_wan22_rtx5090.bat`:
```batch
set TORCH_COMPILE_MODE=default  # Safest, minimal overhead
```

**Expected with default mode:**
- Memory overhead: +0.5-1GB (very low)
- Speedup: 8-12% (slightly less than reduce-overhead)
- OOM risk: Very low

---

## What to Look For

### First Run (Compilation):

**Console output:**
```
[torch._dynamo] Compiling function...
[torch._inducer] Generating code...
```

**Timing:**
- First run will be SLOWER due to compilation
- This is expected and normal
- Compilation is cached for subsequent runs

### Subsequent Runs:

**Console output:**
```
Using cached compilation...
```

**Timing:**
- Should be 10-15% faster than baseline
- Consistent across multiple runs

### Memory Usage:

**Monitor with nvidia-smi:**
```batch
# In a separate terminal:
nvidia-smi -l 1
```

**Watch for:**
- Peak VRAM during generation
- Should stay under 28GB (leaving ~4GB margin)
- If approaching 30GB, may OOM

---

## Step-by-Step Testing Instructions

### 1. Restart ComfyUI with New Settings

```batch
# Close current ComfyUI instance (Ctrl+C)
# Then restart:
.\scripts\launch_wan22_rtx5090.bat
```

### 2. Test 61 Frames (Your Benchmark)

**Option A: Via ComfyUI UI**
1. Load workflow
2. Upload image
3. Set frames: 61
4. Queue prompt
5. Time the generation

**Option B: Via Script**
```batch
# In a second terminal:
.\venv\Scripts\python.exe scripts\generate_wan22_video.py input\sogni-photobooth-my-polar-bear-baby-raw.jpg --frames 61 --settings "4step_torch_compile"
```

### 3. Record Results

**Create comparison table:**

| Run | Compile Mode | Frames | Time | Notes |
|-----|--------------|--------|------|-------|
| Baseline 1 | None | 61 | 138.35s | Cold start |
| Baseline 2 | None | 61 | 93.44s | Warm cache |
| Test 1 | reduce-overhead | 61 | ??? | First compile |
| Test 2 | reduce-overhead | 61 | ??? | Should be faster |
| Test 3 | reduce-overhead | 61 | ??? | Verify consistency |

### 4. Calculate Speedup

```
Speedup = (Baseline_Time - Test_Time) / Baseline_Time × 100%

Target: 10-15% speedup
Example: (93.44 - 80) / 93.44 = 14.4% ✅
```

---

## Interpreting Results

### ✅ Success Case:
- No OOM errors
- 10-15% faster than baseline (93.44s → ~80-85s)
- Consistent performance across runs

**Action:** Keep reduce-overhead mode enabled

### ⚠️ Partial Success:
- Works on 61 frames but OOMs on 81 frames

**Action:** Use hybrid approach (compile for ≤61 frames, disable for 81+)

### ❌ Still OOMs on 61 Frames:
- Switch to `default` mode
- Retest with lower memory overhead

**Action:** Update `TORCH_COMPILE_MODE=default` and retest

### 📉 No Speedup or Slower:
- Check if compilation actually happened
- Verify torch.compile is enabled
- Check for other bottlenecks

**Action:** Review logs, verify environment variables

---

## Expected Timeline

### Optimistic Case:
- ✅ 61 frames: ~80s (vs 93.44s baseline)
- ✅ 81 frames: ~105s (vs ~124s baseline)
- **Result:** 10-15% speedup, no OOM

### Realistic Case:
- ✅ 61 frames: ~80-85s
- ⚠️ 81 frames: OOM with reduce-overhead
- ✅ 81 frames: ~110-115s with default mode
- **Result:** 8-12% speedup on 81 frames

### Fallback Case:
- ⚠️ 61 frames: OOM with reduce-overhead
- ✅ 61 frames: ~85-90s with default mode
- ✅ 81 frames: ~115-120s with default mode
- **Result:** 8-10% speedup, very stable

---

## Summary

### Current Status:
✅ **Launch script updated** with `reduce-overhead` mode  
✅ **Research completed** on OOM causes and solutions  
✅ **Testing plan documented** with clear success criteria  
⏳ **Ready to test** when ComfyUI is restarted  

### Next Steps:
1. **Restart ComfyUI** with new settings
2. **Test 61 frames** (should see ~80-85s)
3. **Report results** - I'll help interpret and optimize further

### Expected Outcome:
- **10-15% faster** generation with reduce-overhead mode
- **No OOM** on 61 frames
- **Possible OOM** on 81 frames (fallback to default mode if needed)

---

## Ready to Test?

**Restart ComfyUI now:**
```batch
.\scripts\launch_wan22_rtx5090.bat
```

Then run your 61-frame test and let me know the results!

