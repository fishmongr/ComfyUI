# Wan 2.2 i2v System Audit - RTX 5090

**Date**: November 23, 2025

## Hardware Configuration

### GPU
- **Model**: NVIDIA GeForce RTX 5090
- **Architecture**: Blackwell
- **VRAM**: 32,607 MiB (32GB)
- **Driver Version**: 580.97
- **Power Limit**: 600W
- **Current Clocks**: 457 MHz (Graphics), 405 MHz (Memory) - idle state

### CUDA & PyTorch
- **CUDA Version**: 12.8
- **PyTorch Version**: 2.10.0.dev20251121+cu128 (Development build with CUDA 12.8)
- **CUDA Available**: Yes
- **GPU Detection**: Working correctly

### System Configuration
- **OS**: Windows 10.0.26100
- **Power Plan**: High Performance ✓
- **Shell**: PowerShell 7

## Environment Variables (Performance-Related)

### Current Settings
- `TORCH_COMPILE=0` ⚠️ **IMPORTANT**: Torch compile is DISABLED
  - This may be contributing to performance variations
  - Should test with compile enabled for potential speedup
- `TORCH_COMPILE_MODE=max-autotune`
  - Mode is set but compile is disabled
- `COMPOSER_NO_INTERACTION=1` (not relevant to performance)

### Missing/Not Set
- `PYTORCH_CUDA_ALLOC_CONF` - Not set (could optimize CUDA memory allocation)
- `CUDA_LAUNCH_BLOCKING` - Not set (good, async execution enabled)
- `OMP_NUM_THREADS` - Not explicitly set
- `CUDA_MODULE_LOADING` - Not set

## Wan 2.2 Models & Assets

### Models (models/diffusion_models/)
- ✓ `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors`
- ✓ `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors`

### LoRAs (models/loras/)
- ✓ `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors`
- ✓ `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors`

### VAE (models/vae/)
- ✓ `wan_2.1_vae.safetensors`

### Text Encoder (models/text_encoders/)
- ✓ `umt5_xxl_fp8_e4m3fn_scaled.safetensors`

## Test Images Available

Located in `input/` folder:
- sogni-photobooth-my-polar-bear-baby-raw.jpg
- 131102~1.PNG
- download.jpg (and download-1.jpg through download-12.jpg)
- 3d/ subfolder

**Recommendation**: Select 3 diverse images for benchmarking:
1. sogni-photobooth-my-polar-bear-baby-raw.jpg (portrait/character)
2. One from download-*.jpg series (general scene)
3. One from 3d/ folder if available (different content type)

## Custom Nodes Installed

- ✓ ComfyUI-SageAttention3 (attention optimization for Blackwell/Ada)
- ✓ ComfyUI-TeaCache (tested, rejected for quality loss)
- ✓ ComfyUI-Manager (node management)
- ✓ ComfyUI-KJNodes (utility nodes)

## Performance Baseline (User's Manual Testing)

### 832x1216 Resolution
- **No LoRA**: 595s for 49 frames (3s video)
- **With 4-step LoRA**: 67-83s range (target performance)
  - Runs: 83.14s, 73.7s, 81s, 69s, 80s, 67s
- **Performance degradation observed**: 126s first, 114s second
  - May be related to TORCH_COMPILE=0 setting
  - Could be testing methodology variation

### Target Performance
- **Per pass**: 67-80s for 5s video (81 frames) @ 832x1216
- **Two-pass total**: 134-160s
- **With interpolation**: < 180s for 5s@32fps

## Key Findings

### Strengths
✓ Excellent hardware (RTX 5090, 32GB VRAM)
✓ Correct CUDA 12.8 + PyTorch 2.10 for Blackwell support
✓ High Performance power plan enabled
✓ All required models and LoRAs present
✓ --disable-pinned-memory likely needed (typical for RTX 50 series)

### Areas for Investigation
⚠️ **TORCH_COMPILE=0**: Torch compile disabled - should test impact
⚠️ **Performance variation**: Need systematic testing to identify cause
⚠️ **Missing optimizations**: Haven't tested SageAttention3 impact yet
⚠️ **Environment variables**: Could optimize PYTORCH_CUDA_ALLOC_CONF

## Next Steps

1. Create optimized launch script with recommended flags
2. Test with TORCH_COMPILE enabled vs disabled
3. Build automated testing framework
4. Run systematic baseline tests
5. Test optimization combinations
6. Document reproducible configuration

## Notes

- **Two-pass workflow**: high_noise + low_noise models used sequentially for best quality
- **Frame rate**: Generate at 16fps (model training rate), interpolate to 32fps
- **4-step LoRA**: Always enabled (user-validated quality/speed trade-off)
- **Frame conditioning**: Will implement first frame, last frame, first+last modes

