# SageAttention3 Testing - Next Steps

## ✅ SageAttention3 Enabled!

I've successfully enabled SageAttention3 in the workflow:
- **Node 117**: Enabled (high_noise model path)
- **Node 118**: Enabled (low_noise model path)

## 🔄 Restart Required

ComfyUI needs to be restarted to load the updated workflow. Please:

### Step 1: Restart ComfyUI

```bash
# Stop the current ComfyUI process (Ctrl+C in the terminal where it's running)
# Then restart with:
.\scripts\launch_wan22_rtx5090.bat
```

### Step 2: Open the workflow in ComfyUI web interface
1. Go to http://localhost:8188
2. Load the workflow: `user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json`
3. Verify nodes 117 and 118 show "enable: true"

### Step 3: Run the SageAttention3 benchmarks

Once ComfyUI is running, I'll automatically run these tests:

```bash
# Quick test (25 frames)
python scripts/generate_wan22_video.py input/sogni-photobooth-my-polar-bear-baby-raw.jpg --frames 25 --settings "4step_sage3"

# Full benchmark suite
python scripts/wan22_benchmark.py --test-frames 25,49,81 --settings "4step_sage3" --output benchmarks/rtx5090_sage3.csv
```

---

## Expected Results with SageAttention3

Based on Blackwell (RTX 5090) optimizations:

| Frames | Baseline (no SageAttention3) | Expected (SageAttention3) | Improvement |
|--------|------------------------------|---------------------------|-------------|
| 25 | 40.61s | **32-36s** | 10-20% faster |
| 49 | 81.17s | **65-73s** | 10-20% faster |
| 81 | 161.70s | **129-145s** | 10-20% faster |

**Key benefits:**
- 10-20% speed improvement (Blackwell optimization)
- 10-20% reduction in activation memory
- May allow 161 frames without offloading to RAM

---

## What I'll Test

1. **Performance comparison:**
   - 25, 49, 81, and 161 frames
   - Compare to baseline results
   - Measure speedup percentage

2. **Memory usage:**
   - Check if 161 frames still offloads to RAM
   - Monitor VRAM usage during generation

3. **Quality validation:**
   - Generate side-by-side comparisons
   - Verify no quality degradation

---

## Ready When You Are!

Just restart ComfyUI and let me know when it's running. I'll then automatically:
1. Test 25 frames to verify SageAttention3 is working
2. Run full benchmark suite (25, 49, 81 frames)
3. Test 161 frames to see if it resolves the RAM offloading issue
4. Generate comparison report


