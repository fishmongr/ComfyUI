# Quick Start Guide - Wan 2.2 i2v Optimization

## Current Status ✅

Your ComfyUI setup is now optimized and ready for Wan 2.2 i2v video generation on RTX 5090!

**Key achievements:**
- ✅ Optimized launch scripts for RTX 5090, 4090, and A100
- ✅ Automated video generation script working
- ✅ Dynamic filename generation
- ✅ OOM issues resolved
- ✅ Benchmark framework ready

---

## Quick Commands

### 1. Start ComfyUI (RTX 5090 Optimized)

```bash
.\scripts\launch_wan22_rtx5090.bat
```

This launches ComfyUI with:
- `--normalvram` - Dynamic VRAM management
- `--reserve-vram 4` - Reserve 4GB for activation memory
- `TORCH_COMPILE=0` - Disable compile overhead
- Optimized CUDA memory allocation

### 2. Generate a Single Video

```bash
# Basic usage (25 frames @ 832x1216)
python scripts/generate_wan22_video.py input/your-image.jpg

# Custom frame count (49 frames = 3s)
python scripts/generate_wan22_video.py input/your-image.jpg --frames 49

# Custom resolution
python scripts/generate_wan22_video.py input/your-image.jpg --frames 81 --width 1024 --height 1024

# Full options
python scripts/generate_wan22_video.py input/your-image.jpg \
    --frames 81 \
    --width 832 \
    --height 1216 \
    --settings "4step_nosage" \
    --timeout 600
```

**Output location:** `output/video/`  
**Filename format:** `sourcename_832x1216_25f_1.6s_4step_nosage_20251123_120530.mp4`

### 3. Run Benchmarks

```bash
# Quick test (25, 49, 81 frames)
python scripts/wan22_benchmark.py

# Custom frame counts
python scripts/wan22_benchmark.py --test-frames 25,49,81,161

# Custom output location
python scripts/wan22_benchmark.py --output benchmarks/my_test.csv

# Full options
python scripts/wan22_benchmark.py \
    --image input/test-image.jpg \
    --test-frames 25,49,81 \
    --width 832 \
    --height 1216 \
    --output benchmarks/rtx5090_baseline.csv \
    --timeout 600
```

**Output:**
- CSV file with detailed metrics
- Summary report with statistics
- Location: `benchmarks/` folder

---

## What's Been Optimized

### Launch Configuration (RTX 5090)

**Settings:**
```batch
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True
TORCH_COMPILE=0
OMP_NUM_THREADS=8
CUDA_MODULE_LOADING=LAZY

--normalvram
--reserve-vram 4
--cuda-malloc
--preview-method auto
```

**Why these settings:**
- `--normalvram` - Dynamically manages VRAM, offloads models when needed
- `--reserve-vram 4` - Keeps 4GB free for activation memory (prevents OOM)
- `--cuda-malloc` - Uses optimized CUDA memory allocator
- `TORCH_COMPILE=0` - Avoids torch.compile memory overhead
- `max_split_size_mb:512` - Better memory fragmentation handling

### Workflow Configuration

**Current settings:**
- 4-step LoRA: **Enabled** (8x speedup, user-validated quality)
- SageAttention3: **Disabled** (caused OOM on initial tests)
- Models: fp8_scaled (high_noise + low_noise)
- VAE: wan_2.1_vae.safetensors
- Text Encoder: umt5_xxl_fp8_e4m3fn_scaled.safetensors

**Two-pass workflow:**
1. Pass 1 (high_noise model): Generates initial video with 4-step LoRA
2. Pass 2 (low_noise model): Refines video with 4-step LoRA
3. Result: Single high-quality video

---

## Next Steps

### Immediate Testing (Do This First)

1. **Baseline Benchmark**
   ```bash
   python scripts/wan22_benchmark.py --test-frames 25,49,81
   ```
   This will establish your baseline performance on RTX 5090.

2. **Review Results**
   - Check `benchmarks/benchmark_TIMESTAMP.csv` for detailed metrics
   - Check `benchmarks/summary_report.txt` for readable summary
   - Compare to target: 67-80s per pass for 81 frames

3. **Test Maximum Frame Count**
   ```bash
   python scripts/generate_wan22_video.py input/your-image.jpg --frames 161 --timeout 900
   ```
   This tests 10s videos (161 frames @ 16fps).

### Optional Optimizations to Test

1. **SageAttention3 (Blackwell-Optimized)**
   - Edit workflow: Set nodes 117 and 118 `enable=true`
   - Reload in ComfyUI
   - Run benchmark again
   - Compare performance vs quality

2. **Different Frame Counts**
   ```bash
   python scripts/wan22_benchmark.py --test-frames 25,49,81,121,161
   ```

3. **Different Resolutions**
   ```bash
   python scripts/wan22_benchmark.py --width 1024 --height 1024 --test-frames 49,81
   ```

### Frame Interpolation (Phase 2)

**Goal:** 16fps → 32fps using RIFE or FILM

**Next steps:**
1. Install frame interpolation custom nodes
2. Create interpolation workflows
3. Benchmark RIFE vs FILM
4. Target: < 20s overhead for 81→162 frames

### Docker Deployment (Phase 3)

**Goal:** Create optimized Docker containers for Sogni distributed rendering

**Files to create:**
- `docker/Dockerfile.wan22` - Multi-stage build
- `docker/docker-compose.yml` - Service definitions
- `docker/README.md` - Deployment guide

---

## Troubleshooting

### OOM Errors

If you encounter OOM errors:

1. **Reduce frame count**
   ```bash
   python scripts/generate_wan22_video.py input/image.jpg --frames 25
   ```

2. **Increase reserved VRAM**
   Edit `scripts/launch_wan22_rtx5090.bat`:
   ```batch
   --reserve-vram 6
   ```

3. **Check VRAM usage**
   - Open ComfyUI web interface
   - Check bottom status bar for VRAM usage

### Slow Performance

If generation is slower than expected (> 100s for 81 frames):

1. **Check TORCH_COMPILE setting**
   Should be `TORCH_COMPILE=0` in launch script

2. **Verify 4-step LoRA is enabled**
   Open workflow in ComfyUI, check LoRA nodes 101 and 102

3. **Check for background processes**
   - Close other GPU-intensive apps
   - Check Windows Task Manager → GPU usage

### Script Errors

If scripts fail to run:

1. **Ensure ComfyUI is running**
   ```bash
   curl http://localhost:8188/system_stats
   ```

2. **Check Python environment**
   ```bash
   python --version  # Should be 3.10+
   ```

3. **Verify image exists**
   ```bash
   dir input\your-image.jpg
   ```

---

## Performance Targets

### RTX 5090 (Your GPU)
- **25 frames (1.6s)**: ~30-40s per pass
- **49 frames (3.0s)**: ~50-70s per pass
- **81 frames (5.0s)**: ~67-80s per pass (target)
- **161 frames (10s)**: ~150-200s per pass

### Two-Pass Total Time
- **5s video**: 134-160s (both passes)
- **10s video**: ~300-400s (both passes)

### With Frame Interpolation (Future)
- **5s @ 32fps**: < 180s total (including interpolation)

---

## Files Reference

### Scripts
- `scripts/launch_wan22_rtx5090.bat` - Launch ComfyUI (RTX 5090)
- `scripts/generate_wan22_video.py` - Generate single video
- `scripts/wan22_benchmark.py` - Run automated benchmarks
- `scripts/save_env.py` - Capture environment snapshot

### Workflows
- `user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json` - Current workflow

### Documentation
- `docs/CURRENT_STATUS.md` - Full status and progress
- `docs/QUICK_START.md` - This guide
- `docs/env_snapshot_rtx5090.json` - System configuration

### Output
- `output/video/` - Generated videos
- `benchmarks/` - Benchmark results and reports

---

## Getting Help

If you encounter issues:

1. **Check the logs**
   - ComfyUI console output
   - Script error messages

2. **Review documentation**
   - `docs/CURRENT_STATUS.md` - Full project status
   - `docs/OOM_RESOLUTION.md` - OOM troubleshooting history

3. **Test with minimal settings**
   ```bash
   python scripts/generate_wan22_video.py input/image.jpg --frames 25
   ```

---

## What's Working Now ✅

- ✅ Automated video generation
- ✅ Dynamic filename generation
- ✅ Two-pass workflow (high_noise + low_noise)
- ✅ 4-step LoRA enabled by default
- ✅ OOM protection with reserved VRAM
- ✅ Benchmark framework ready
- ✅ Progress monitoring
- ✅ RTX 5090, 4090, and A100 launch scripts

## What's Next 🎯

- 🎯 Run baseline benchmarks
- 🎯 Test SageAttention3 performance
- 🎯 Add frame interpolation (RIFE/FILM)
- 🎯 Create Docker containers
- 🎯 Full documentation suite

---

**Ready to start?** Run your first benchmark:

```bash
python scripts/wan22_benchmark.py --test-frames 25,49,81
```

This will test 1.6s, 3.0s, and 5.0s videos and give you baseline performance metrics!


