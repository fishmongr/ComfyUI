# Wan 2.2 i2v Optimization - Getting Started Guide

## Quick Start

### 1. Launch ComfyUI with Optimized Settings

For RTX 5090:
```cmd
scripts\launch_wan22_rtx5090.bat
```

For RTX 4090:
```cmd
scripts\launch_wan22_rtx4090.bat
```

For A100:
```cmd
scripts\launch_wan22_a100.bat
```

### 2. Access ComfyUI Web Interface

Open your browser to: http://localhost:8188

### 3. Load Wan 2.2 i2v Workflow

Navigate to `workflows/` directory and load one of the following:
- `wan22_i2v_twopass_baseline.json` - Basic two-pass i2v workflow
- `wan22_i2v_first_frame.json` - First frame conditioning
- `wan22_i2v_last_frame.json` - Last frame conditioning  
- `wan22_i2v_first_last_frame.json` - First and last frame conditioning
- `wan22_i2v_twopass_rife.json` - With RIFE interpolation (16fps → 32fps)
- `wan22_i2v_twopass_film.json` - With FILM interpolation (16fps → 32fps)

## Understanding Wan 2.2 Two-Pass Workflow

Wan 2.2 i2v uses both high_noise and low_noise models sequentially for best quality:

**Pass 1**: First model generates initial video from input image  
**Pass 2**: Second model refines the video for better quality

### Model Files Required

Located in `models/diffusion_models/`:
- `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` ✓
- `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` ✓

Located in `models/loras/`:
- `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` ✓ (Always enabled)
- `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` ✓ (Always enabled)

Located in `models/vae/`:
- `wan_2.1_vae.safetensors` ✓

Located in `models/text_encoders/`:
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors` ✓

## Performance Targets

### RTX 5090 (32GB VRAM)
- **Per pass**: 67-80s for 5s video (81 frames) @ 832x1216
- **Two-pass total**: 134-160s
- **With interpolation**: < 180s for 5s@32fps

### RTX 4090 (24GB VRAM)
- **Per pass**: 80-100s
- **Two-pass total**: 160-200s
- Note: VRAM management required for 10s videos

### A100 (40/80GB VRAM)
- **Per pass**: 75-95s (with FlashAttention)
- **Two-pass total**: 150-190s

## Frame Conditioning Modes

### First Frame Only (Standard i2v)
Provide starting frame, model generates forward motion.

### Last Frame Only
Provide ending frame, model generates motion leading to it.

### First + Last Frame
Provide both frames, model generates smooth transition between them.  
**Use cases**: Keyframe animation, controlled transitions, storyboarding

## Environment Variables (Already Set in Launch Scripts)

### Performance Optimization
```cmd
set TORCH_COMPILE=1
set TORCH_COMPILE_MODE=max-autotune
set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:512
set OMP_NUM_THREADS=8
set CUDA_MODULE_LOADING=LAZY
```

### If You Need to Change Settings

Edit the appropriate launch script:
- `scripts/launch_wan22_rtx5090.bat`
- `scripts/launch_wan22_rtx4090.bat`
- `scripts/launch_wan22_a100.bat`

## Running Benchmarks

### Prerequisites
1. ComfyUI must be running (use launch script)
2. Test images in `input/` folder
3. Install dependencies: `pip install websocket-client requests Pillow numpy`

### Run Baseline Tests
```cmd
cd scripts
python wan22_benchmark.py
```

This will:
- Test both pass orders (high→low, low→high)
- Test both durations (5s and 10s)
- Test on 3 images from input folder
- Generate performance metrics
- Create HTML report with results
- Alert if performance degrades (> 85s per pass)

### View Results
```
benchmark_results/
├── logs/           - JSON logs with detailed metrics
├── reports/        - HTML comparison reports
└── videos/         - Generated test videos
```

## Troubleshooting

### ComfyUI Won't Start
- Check that venv is activated
- Verify CUDA 12.8+ is installed for RTX 5090
- Ensure PyTorch 2.7.0+ is installed
- Try with `--verbose DEBUG` flag for more info

### Out of Memory (OOM) Errors
- **RTX 4090 users**: Use `--normalvram` instead of `--highvram`
- Reduce video length (try 5s before 10s)
- Close other GPU-intensive applications
- Check task manager for GPU memory usage

### Slow Performance
- Verify High Performance power plan (Windows)
- Check environment variables are set correctly
- Run `scripts/save_env.py` to snapshot working config
- Monitor GPU temperature (throttles at 83°C+)
- Verify 4-step LoRA is loading correctly

### Quality Issues
- Ensure both passes are completing
- Verify correct pass order (test both to compare)
- Check if models are fp8_scaled versions
- Review prompt and negative prompt
- Compare with/without interpolation

## Advanced: Environment Management

### Save Current Configuration
```cmd
python scripts/save_env.py
```

Creates `scripts/environment_snapshot.json` with:
- Environment variables
- GPU stats
- PyTorch/CUDA versions
- System info

### Restore Previous Configuration
```cmd
python scripts/restore_env.py
```

Generates `scripts/restore_env.bat` to restore environment variables.

## Next Steps

1. ✓ Launch ComfyUI with optimized settings
2. ✓ Load a workflow template
3. ✓ Generate test video
4. Run benchmarks to establish baseline
5. Test frame interpolation (RIFE vs FILM)
6. Review optimization results
7. Deploy to Docker for Sogni distributed rendering

## Support & Documentation

- **System Audit**: `docs/SYSTEM_AUDIT.md`
- **Optimization Guide**: `docs/OPTIMIZATION_GUIDE.md` (after Phase 4)
- **Benchmark Results**: `docs/BENCHMARK_RESULTS.md` (after testing)
- **Plan**: `w.plan.md` (project roadmap)

## Key Reminders

✓ **Always use 4-step LoRA** (enabled by default in workflows)  
✓ **16fps generation** (model training rate, interpolate to 32fps)  
✓ **Two-pass workflow** (both models required for best quality)  
✓ **Target resolution**: 832x1216 @ 16fps  
✓ **Monitor VRAM** (especially on RTX 4090)

