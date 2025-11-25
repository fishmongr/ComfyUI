# OOM Testing Results

## Test Summary

Testing various configurations to isolate the OOM error on RTX 5090 (32GB VRAM).

## Test Configurations

### Test 1: Original Workflow (49 frames, SageAttention3 enabled)
- **Status**: ❌ OOM Error
- **VRAM Loaded**: ~20.3 GB (Text: 6.4 GB, VAE: 0.24 GB, Model: 13.6 GB)
- **Expected Free**: ~11.7 GB
- **Conclusion**: OOM during attention despite sufficient apparent VRAM

### Test 2: Diagnostic Launch (49 frames, TORCH_COMPILE=0, SageAttention3 enabled)
- **Status**: ❌ OOM Error
- **Configuration**: `TORCH_COMPILE=0` to rule out torch.compile overhead
- **Conclusion**: torch.compile was not the issue

### Test 3: No SageAttention3 (25 frames, reduced for safety)
- **Status**: 🧪 Testing
- **Changes**:
  - SageAttention3 nodes 117 & 118: `enable=false`
  - Frame count reduced from 49 to 25 (50% reduction)
  - Filename prefix changed to `ComfyUI_NO_SAGE_25frames`
- **Hypothesis**: SageAttention3 is allocating extra buffers that push VRAM over capacity
- **File**: `user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json`

## Next Steps

1. **Run Test 3**: Load the `video_wan2_2_14B_i2v_no_sage_test.json` workflow in ComfyUI
2. **If Test 3 succeeds**: 
   - SageAttention3 is incompatible with RTX 5090 + PyTorch 2.10 dev
   - Document workaround: Use PyTorch native attention
   - Test increasing frame count back to 49 without SageAttention3
3. **If Test 3 fails**:
   - Try further reducing frame count to 17 (1 second @ 16fps)
   - Check for memory leaks or fragmentation
   - Consider model quantization issues (fp8 precision)

## Logs & Evidence

- Launch script: `scripts/launch_wan22_diagnostic.bat`
- Environment snapshot: `docs/env_snapshot_rtx5090.json`
- Detailed troubleshooting: `docs/OOM_TROUBLESHOOTING.md`

## Expected Outcome

With 32GB VRAM and only ~20GB used for models, a properly configured system should handle 49 frames (3s video) comfortably. The OOM suggests either:
1. SageAttention3 memory overhead
2. Attention activation memory calculation issue
3. VRAM fragmentation
4. Driver/CUDA compatibility issue with Blackwell architecture

---
**Last Updated**: 2025-11-23  
**Tester**: AI Assistant (automated)

