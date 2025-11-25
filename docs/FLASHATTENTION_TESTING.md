# FlashAttention Testing Guide - RTX 5090

## Quick Start

### Step 1: Launch ComfyUI with FlashAttention

Open a terminal and run:

```batch
cd C:\Users\markl\Documents\git\ComfyUI
.\scripts\launch_wan22_rtx5090.bat
```

**What to look for in the logs:**
```
Using pytorch attention
```

This confirms FlashAttention is enabled via PyTorch SDPA.

---

### Step 2: Run Test Generation (Option A - Manual UI)

1. Open ComfyUI UI: http://localhost:8188
2. Load workflow: `user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json`
3. Upload test image: `input/sogni-photobooth-my-polar-bear-baby-raw.jpg`
4. Set frames: **25** (quick test) or **81** (full test)
5. Click "Queue Prompt"
6. **Time the generation** and note VRAM usage

---

### Step 3: Run Test Generation (Option B - Automated Script)

**In a SECOND terminal** (while ComfyUI is running):

```batch
cd C:\Users\markl\Documents\git\ComfyUI
.\venv\Scripts\python.exe scripts\generate_wan22_video.py input\sogni-photobooth-my-polar-bear-baby-raw.jpg --frames 25 --settings "4step_flash_test"
```

---

## Benchmark Comparison

### Baseline (No FlashAttention)
**Without `--use-pytorch-cross-attention`:**
- 25 frames: ~25s
- 81 frames (5s): ~75s per pass
- Attention: `sub quadratic optimization`

### With FlashAttention (PyTorch SDPA)
**With `--use-pytorch-cross-attention`:**
- 25 frames: **~20-23s** (expected)
- 81 frames (5s): **~60-70s** per pass (expected)
- Attention: `pytorch attention` (using FlashAttention backend)

**Expected Speedup:** 10-20% reduction in generation time

---

## Full Benchmark Suite

Once you confirm FlashAttention is working:

```batch
.\venv\Scripts\python.exe scripts\wan22_benchmark.py --test-frames 25,49,81 --settings "4step_flash" --output benchmarks\rtx5090_flashattn.csv
```

Compare results:
- `benchmarks\rtx5090_flashattn.csv` (with FlashAttention)
- vs previous baseline runs

---

## Verification Checklist

✅ **ComfyUI logs show:** `Using pytorch attention`  
✅ **Generation completes** without errors  
✅ **Timing improved** by 10-20% vs baseline  
✅ **VRAM usage** similar or slightly better  
✅ **Output quality** unchanged  

---

## Troubleshooting

### Issue: Still shows "Using sub quadratic optimization"

**Solution:** Verify launch script has `--use-pytorch-cross-attention`:
```batch
python main.py ^
  --use-pytorch-cross-attention ^
  --normalvram ^
  --reserve-vram 4 ^
  ...
```

### Issue: Performance same or worse

**Possible causes:**
1. Bottleneck is not attention (e.g., VAE decode, LoRA)
2. Sequence length too short (< 49 frames)
3. Other processes using GPU

**Next step:** Try frame interpolation instead (bigger win)

---

## Current Setup Summary

✅ **FlashAttention Status:** Enabled via PyTorch SDPA  
✅ **Launch Script:** Updated with `--use-pytorch-cross-attention`  
✅ **PyTorch Version:** 2.10.0.dev20251121+cu128  
✅ **CUDA Version:** 12.8  
✅ **SDPA Backends:** flash_sdp ✓, mem_efficient_sdp ✓, math_sdp ✓  

---

## Next Steps After Testing

1. **If FlashAttention shows 10-20% speedup:**
   - ✅ Keep it enabled
   - ⏭️ Move to Frame Interpolation (RIFE/FILM)

2. **If FlashAttention shows minimal gains:**
   - ✅ Keep it enabled anyway (no downside)
   - ⏭️ Move to Frame Interpolation (bigger win)

3. **Frame Interpolation = Next Priority**
   - 16fps → 32fps doubling
   - Expected: < 20s for 81 → 162 frames
   - **Bigger performance impact than attention optimization**

---

## Ready to Test?

**Run this now:**
```batch
.\scripts\launch_wan22_rtx5090.bat
```

Then let me know when ComfyUI is running and I'll help you run the benchmark!

