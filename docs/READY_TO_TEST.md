# Ready to Test - DeleteModelPassthrough on RTX 5090

## Current Status: ✅ READY

All setup complete. Ready for testing.

## What Changed Since Last Test

### 1. ✅ Installed DeleteModelPassthrough
Custom node that **aggressively deletes models from VRAM and RAM** (not just cache clearing).

### 2. ✅ Integrated into Workflow
Node 119 now sits between KSampler 86 (High Noise Pass) and KSampler 85 (Low Noise Pass).

### 3. ✅ Bypassed SageAttention3
Nodes 117 and 118 are set to mode 4 (bypassed) due to build issues.
- Using **PyTorch SDPA** (default, already optimized for RTX 5090)
- No performance impact - you were already at 124-137s baseline

## Expected Test Results

### 81 Frames @ 832x1216
| Metric | Before | After (Target) |
|--------|--------|----------------|
| High Noise Pass | ~19GB VRAM | ~19GB VRAM |
| Between Passes | ~19GB (model in RAM) | **~6GB (model deleted)** |
| Low Noise Pass | 32GB+ needed → **845MB offload** | **~19GB (no offload)** |
| Total Time | 146-153s | **124-137s** (~20-30s faster) |

### 161 Frames @ 832x1216
| Metric | Before | After (Target) |
|--------|--------|----------------|
| Status | OOM/Untested | **Should work!** |
| Total Time | N/A | **~250-270s** (2x the 81-frame time) |

## Quick Test Procedure

```powershell
# 1. Restart ComfyUI
taskkill /IM python.exe /F
.\scripts\launch_wan22_rtx5090.bat

# 2. Load workflow in UI
#    File: video_wan2_2_14B_i2v_no_sage_test.json
#    Verify "Delete High Noise Model" node exists

# 3. Run 81-frame test
#    Watch console for:
#      ✅ "Using pytorch attention" (on startup)
#      ✅ NO "sage attention" messages
#      ✅ "Deleting model from VRAM and RAM..." (between passes)
#      ✅ NO "Loaded to offload" messages

# 4. Check results
#    Target: 124-137s (vs. previous 146-153s)
```

## What to Look For

### ✅ Success Indicators
1. Console shows "Using pytorch attention" on startup
2. Console shows model deletion message between passes
3. **NO "offload" messages in logs**
4. VRAM drops to ~6GB between passes (use nvidia-smi)
5. Total time: **124-137s** for 81 frames
6. Video quality unchanged

### ❌ Failure Indicators
1. Console shows "Loaded to offload" messages
2. VRAM stays at ~19GB between passes
3. Total time: 146-153s (same as before)
4. OOM errors

## Files Ready for Testing

```
✅ user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json
   - DeleteModelPassthrough (Node 119) added
   - SageAttention3 (Nodes 117, 118) bypassed

✅ custom_nodes/ComfyUI_DeleteModelPassthrough/
   - Installed and ready

✅ scripts/launch_wan22_rtx5090.bat
   - Optimized settings (--normalvram, --reserve-vram 2)

✅ Documentation:
   - docs/DELETE_MODEL_TEST_GUIDE.md (detailed test steps)
   - docs/DELETE_MODEL_STATUS.md (status summary)
   - docs/SAGEATTENTION3_DISABLED.md (why SageAttention is disabled)
```

## Why This Should Work

### Previous Attempts (Failed to Eliminate Offload):
| Method | What It Does | Why It Failed |
|--------|--------------|---------------|
| `easy cleanGpuUsed` | Clears CUDA cache | Doesn't remove model weights |
| `easy clearCacheAll` | Clears ComfyUI caches | Doesn't remove model weights |
| ComfyUI default | Moves models to RAM | Both models stay loaded (32GB+ total) |

### DeleteModelPassthrough (Should Succeed):
| What It Does | Why It Should Work |
|--------------|-------------------|
| `del model` | Removes Python object reference |
| `torch.cuda.empty_cache()` | Clears CUDA memory |
| `gc.collect()` | Python garbage collection |
| **Result:** | **13GB high noise model completely removed from VRAM and RAM** |

## Next Steps After Testing

### If Successful (No 845MB Offload):
1. ✅ Mark DeleteModelPassthrough as **solution for RTX 5090**
2. Test 161 frames (10s video)
3. Test 241 frames (15s video)
4. Add RIFE interpolation (16fps → 32fps)
5. Document as production configuration

### If Unsuccessful (Still Offloading):
1. Check console logs for errors
2. Verify DeleteModelPassthrough executed (look for deletion message)
3. Consider **FramePack** alternative (splits video into chunks)
4. May need to accept 845MB offload as unavoidable for 81+ frames

## Performance Expectations

### Target Performance (RTX 5090, 832x1216):
- **81 frames (5s):** 124-137s ← **YOU WERE HERE before offload started**
- **161 frames (10s):** ~250-270s ← **NEW - should work now**
- **241 frames (15s):** ~375-410s ← **NEW - should work now**

### With RIFE Interpolation (future):
- **81→162 frames (5s @ 32fps):** ~150-170s
- **161→322 frames (10s @ 32fps):** ~280-310s

---

## TL;DR

**You're ready to test!** 

Just restart ComfyUI, load the workflow, run an 81-frame test, and watch for:
1. ✅ "Using pytorch attention" on startup
2. ✅ Model deletion message between passes
3. ✅ **NO "offload" messages**
4. ✅ Time: **124-137s** (vs. previous 146-153s)

If it works, you've unlocked 10-15s videos on RTX 5090! 🚀

---

**Created:** 2024-11-24  
**Status:** Ready for user testing  
**Priority:** HIGH - Critical for longer video generation



