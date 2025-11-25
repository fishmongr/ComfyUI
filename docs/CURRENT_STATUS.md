# Wan 2.2 i2v RTX 5090 Optimization - Current Status

**Date**: 2025-11-23  
**GPU**: NVIDIA GeForce RTX 5090 (32GB VRAM)  
**ComfyUI Version**: 0.3.71  
**PyTorch**: 2.10.0.dev20251121+cu128  
**CUDA**: 12.8

---

## ✅ Completed Tasks

### Phase 1: System Audit & Baseline Setup

1. **Environment Snapshot Created**
   - Script: `scripts/save_env.py`
   - Output: `docs/env_snapshot_rtx5090.json`
   - Captures GPU info, PyTorch version, CUDA version, environment variables

2. **Optimized Launch Scripts Created**
   - `scripts/launch_wan22_rtx5090.bat` (32GB VRAM)
   - `scripts/launch_wan22_rtx4090.bat` (24GB VRAM)
   - `scripts/launch_wan22_a100.bat` (40/80GB VRAM)
   - Configurations:
     - RTX 5090: `--normalvram --reserve-vram 4 --cuda-malloc`
     - RTX 4090: `--normalvram --reserve-vram 4 --cuda-malloc`
     - A100: `--gpu-only --cuda-malloc`
   - Key fixes:
     - Removed `--force-channels-last` (incompatible with 5D video tensors)
     - Removed `--use-sage-attention` (SageAttention3 is a custom node)
     - Set `TORCH_COMPILE=0` to avoid memory overhead
     - Set `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True`

3. **Workflow Configuration**
   - Modified workflow to disable SageAttention3 by default (nodes 117, 118)
   - Set initial test frame count to 25 (1.6s @ 16fps)
   - Configured dynamic filename pattern with source name, resolution, duration, settings
   - Location: `user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json`

4. **Automated Video Generation Script**
   - Script: `scripts/generate_wan22_video.py`
   - Features:
     - Uses actual ComfyUI API format (captured from working prompt)
     - Dynamic filename generation based on source image
     - Automatic duration calculation
     - Progress monitoring
     - Timeout protection
   - Template: `scripts/last_prompt_api_format.json`
   - Usage:
     ```bash
     python scripts/generate_wan22_video.py input/image.jpg --frames 25 --width 832 --height 1216
     ```

5. **Two-Pass Workflow Understanding**
   - Confirmed high_noise + low_noise models work sequentially
   - Both passes use corresponding 4-step LoRAs
   - Pass 1 (high_noise): Generates initial video with noise
   - Pass 2 (low_noise): Refines video for final quality

### Issues Resolved

1. **OOM Error (Channels Last)**
   - Problem: `RuntimeError: required rank 4 tensor to use channels_last format`
   - Cause: `--force-channels-last` incompatible with 5D video tensors
   - Fix: Removed flag from all launch scripts

2. **OOM Error (SageAttention3)**
   - Problem: `torch.OutOfMemoryError` during RoPE operation
   - Cause: SageAttention3 custom node causing VRAM issues
   - Fix: Disabled SageAttention3 nodes in workflow (set `enable=false`)

3. **OOM Error (Activation Memory)**
   - Problem: OOM even with 32GB VRAM when models fully loaded
   - Cause: Insufficient VRAM reserved for activation memory
   - Fix: Changed from `--highvram` to `--normalvram --reserve-vram 4`

4. **Performance Degradation (TORCH_COMPILE)**
   - Problem: Potential memory overhead from torch.compile
   - Fix: Set `TORCH_COMPILE=0` in launch scripts

5. **API Format Conversion Issues**
   - Problem: Complex frontend→API workflow conversion with errors
   - Fix: Captured actual working API format, use as template

---

## 🎯 Current Performance Status

### RTX 5090 (32GB VRAM)
- **Configuration**: 4-step LoRA enabled, SageAttention3 disabled
- **Resolution**: 832x1216
- **Status**: Successfully generating 25 frame (1.6s) videos
- **Launch Command**: `.\scripts\launch_wan22_rtx5090.bat`
- **VRAM Management**: Dynamic with 4GB reserved for activations

### User's Manual Benchmarks (Reference)
- **832x1216, no LoRA, 49 frames (3s)**: 595s baseline
- **832x1216, 4-step LoRA**: 67-83s range (~8x speedup)
- **640x640, 81 frames (5s)**: First run 306s, second 296s
- **With TeaCache**: 42-84s (rejected for quality loss)
- **Target**: 67-80s per pass for two-pass workflow

---

## 📋 Next Steps

### Immediate Tasks (In Progress)

1. **Benchmark Current Setup**
   - Test 25 frames (1.6s) @ 832x1216
   - Test 49 frames (3s) @ 832x1216
   - Test 81 frames (5s) @ 832x1216
   - Measure per-pass timing
   - Document VRAM usage patterns
   - Compare to user's manual benchmarks

2. **Test SageAttention3 (Optional)**
   - Re-enable in workflow
   - Test with same frame counts
   - Compare performance vs quality
   - Determine if worth using on 5090

3. **Test Maximum Frame Count**
   - Find OOM limit with `--reserve-vram 4`
   - Test 161 frames (10s)
   - Document performance scaling

### Phase 2: Frame Interpolation Setup

1. **Install Frame Interpolation Nodes**
   - Research ComfyUI frame interpolation options
   - Install RIFE and FILM nodes
   - Download required models

2. **Create Interpolation Workflows**
   - Build workflow: two-pass + RIFE (16fps → 32fps)
   - Build workflow: two-pass + FILM (16fps → 32fps)
   - Test quality and speed

3. **Benchmark Interpolation**
   - Compare RIFE vs FILM quality
   - Measure interpolation time overhead
   - Target: < 20s for 81→162 frames

### Phase 3: Systematic Optimization Testing

1. **Create Automated Benchmark Script**
   - `scripts/wan22_benchmark.py`
   - Test matrix: multiple images, frame counts, configurations
   - CSV output with timing, VRAM, GPU metrics
   - Error handling and recovery

2. **Test Attention Mechanisms**
   - SageAttention3 (Blackwell-optimized)
   - FlashAttention (`--use-flash-attention`)
   - PyTorch native (`--use-pytorch-cross-attention`)

3. **Test Precision Options**
   - Verify fp8_scaled models
   - Test `--bf16-unet` if applicable

4. **Generate Performance Reports**
   - HTML comparison report
   - User quality review packages
   - Recommendations per GPU tier

### Phase 4: Docker & Documentation

1. **Create Docker Images**
   - `docker/Dockerfile.wan22`
   - Multi-stage build for efficiency
   - GPU-specific configurations
   - Model volume mounts

2. **Documentation**
   - `docs/OPTIMIZATION_GUIDE.md` (GPU-specific)
   - `docs/BENCHMARK_RESULTS.md`
   - `docs/TWO_PASS_WORKFLOW.md`
   - Docker deployment guide

---

## 📊 Performance Targets

### RTX 5090 (32GB VRAM)
- **5s video (81 frames)**: 67-80s per pass = 134-160s total
- **10s video (161 frames)**: < 300s total for two passes
- **With interpolation to 32fps**: < 180s for 5s video

### RTX 4090 (24GB VRAM)
- **5s video (81 frames)**: 80-100s per pass = 160-200s total
- May require VRAM management for 10s videos
- 4-step LoRA essential for 24GB constraint

### A100 (40/80GB VRAM)
- **5s video (81 frames)**: 75-95s per pass (FlashAttention)
- Best for data center deployment
- Batch processing capable

---

## 🔧 Key Configuration Files

### Launch Scripts
- `scripts/launch_wan22_rtx5090.bat` - RTX 5090 optimized
- `scripts/launch_wan22_rtx4090.bat` - RTX 4090 optimized
- `scripts/launch_wan22_a100.bat` - A100 optimized

### Workflows
- `user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json` - Current test workflow

### Scripts
- `scripts/generate_wan22_video.py` - Automated video generation
- `scripts/save_env.py` - Environment snapshot utility
- `scripts/last_prompt_api_format.json` - API template

### Documentation
- `docs/env_snapshot_rtx5090.json` - System configuration
- `docs/SYSTEM_AUDIT.md` - Initial system audit
- `docs/OOM_RESOLUTION.md` - OOM troubleshooting history
- `docs/SAGEATTENTION_NOTE.md` - SageAttention3 notes
- `docs/WORKFLOW_ANALYSIS.md` - Workflow structure analysis
- `docs/FILENAME_GUIDE.md` - Dynamic filename documentation

---

## 🚀 Ready to Use

The system is now ready for:
1. **Automated video generation** via `generate_wan22_video.py`
2. **Performance benchmarking** (ready to implement)
3. **Testing different configurations** (SageAttention3, frame counts, etc.)
4. **Docker containerization** (ready to implement)

**Next immediate action**: Run benchmarks with current configuration to establish baseline performance metrics.


