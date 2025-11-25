# Testing DeleteModelPassthrough - RTX 5090

## What Changed

Installed `ComfyUI-DeleteModelPassthrough` custom node and integrated it into your workflow between the two-pass workflow steps:

**Flow:**
```
High Noise Model (Node 95) 
  -> LoRA (Node 101) 
  -> ModelSamplingSD3 (Node 104) 
  -> Sage3Switch (Node 117) [BYPASSED - using PyTorch attention instead]
  -> KSampler 86 (High Noise Pass)
  -> DeleteModelPassthrough (Node 119) <<< NEW
  -> KSampler 85 (Low Noise Pass)
```

**Note:** SageAttention3 nodes (117, 118) are bypassed due to build issues. PyTorch's native SDPA with FlashAttention is used instead, which is already optimized for RTX 5090.

The `DeleteModelPassthrough` node:
- Takes the LATENT from KSampler 86 (pass-through data)
- Takes the MODEL from Sage3 Node 117 (the high noise model path)
- **COMPLETELY DELETES the high noise model from VRAM and RAM** using `del model`, `torch.cuda.empty_cache()`, and `gc.collect()`
- Passes the LATENT to KSampler 85 (low noise pass)

**Expected Result:** The 845MB offload should be **eliminated** because the 13GB high noise model will be fully deleted before the 13GB low noise model is loaded.

## How This Differs from Previous Attempts

| Method | What It Does | Why It Failed Before |
|--------|--------------|---------------------|
| `easy cleanGpuUsed` | Clears CUDA cache | Doesn't remove model weights |
| `easy clearCacheAll` | Clears ComfyUI internal caches | Doesn't remove model weights |
| ComfyUI default | Moves models to RAM | Both 14B models stay in memory |
| **DeleteModelPassthrough** | **DELETES model from VRAM and RAM** | **Should work!** |

## Test Steps

### 1. Restart ComfyUI

```powershell
# Kill any running ComfyUI processes
taskkill /IM python.exe /F

# Start fresh
.\scripts\launch_wan22_rtx5090.bat
```

**On startup, you should see:**
```
Using pytorch attention
```

This confirms PyTorch SDPA (with FlashAttention) is active. SageAttention3 is bypassed.

### 2. Load the Updated Workflow

Open ComfyUI UI and load:
```
user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json
```

**Verify the DeleteModelPassthrough node exists:**
- Should be visible between KSampler nodes 86 and 85
- Title: "Delete High Noise Model"

### 3. Run 81 Frame Test (5s video)

**Settings:**
- Resolution: 832x1216
- Frames: 81 (length = 73 in workflow, outputs 81 frames)
- Steps: 4
- LoRA: 4-step enabled

**Watch for:**
1. During **High Noise Pass (KSampler 86)**:
   - VRAM usage should be ~19-20GB
2. **After High Noise Pass, BEFORE Low Noise Pass**:
   - Console should show: "Deleting model from VRAM and RAM..."
   - **VRAM should DROP to ~6GB** (only activations remain)
3. During **Low Noise Pass (KSampler 85)**:
   - VRAM should rise to ~19-20GB again
   - **NO "Loaded to offload" message in logs!**

### 4. Check Results

**Success Indicators:**
- Total time: **124-137s** (your previous best)
- **No offloading messages** in console
- VRAM stays at ~19-20GB peak (no 845MB offload)
- Video quality unchanged

**If It Works:**
```powershell
# Document the success
echo "[SUCCESS] DeleteModelPassthrough eliminated offloading at 81 frames!" >> docs/DELETE_MODEL_TEST_RESULTS.txt
echo "Date: %DATE% %TIME%" >> docs/DELETE_MODEL_TEST_RESULTS.txt
echo "Time: [YOUR_TIME_HERE]s" >> docs/DELETE_MODEL_TEST_RESULTS.txt
```

**If It Doesn't Work:**
- Check console logs for errors
- Verify node executed (look for "Deleting model..." message)
- Report back with logs and VRAM observations

### 5. Test Higher Frame Counts

If 81 frames works without offloading:

**Test 161 frames (10s video):**
- Same settings
- **Expected:** Should also work without offloading now
- **Target time:** ~250-270s (2x the 81-frame time)

**Test 241 frames (15s video):**
- Same settings
- **Expected:** Should work if VRAM allows
- **Target time:** ~375-410s (3x the 81-frame time)

## Monitoring Commands

**Real-time VRAM monitoring:**
```powershell
# In a separate PowerShell window
while ($true) { nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader,nounits; Start-Sleep -Seconds 2 }
```

**Check for offloading in logs:**
```powershell
# After the test
Select-String -Path "comfyui.log" -Pattern "offload"
```

## Downsides to Be Aware Of

Per the DeleteModelPassthrough documentation:
1. **Slower reloads:** Models must be loaded from disk if needed again (not applicable for two-pass workflow)
2. **No caching benefit:** ComfyUI can't reuse cached models (not applicable for sequential passes)
3. **Workflow fragility:** If another node expects the model to exist, it may break (not applicable here)

**For your two-pass workflow, these downsides are irrelevant** because:
- Each model is used once per generation
- Models are not reused within a single generation
- No other nodes depend on the high noise model after the first pass

## Expected Performance

### 81 Frames (832x1216)
- **With offload (before):** 146-153s
- **Without offload (target):** 124-137s
- **Improvement:** ~20-30s faster (~15% speedup)

### 161 Frames (832x1216)
- **With offload (before):** Untested (likely caused OOM)
- **Without offload (target):** ~250-270s
- **Improvement:** Should now be possible!

## Next Steps After Testing

1. **If successful:** Update the plan to include DeleteModelPassthrough in all workflows
2. **If successful:** Test with RIFE frame interpolation (16fps -> 32fps)
3. **If successful:** Document as the recommended RTX 5090 configuration
4. **If not successful:** Investigate FramePack as an alternative for longer videos

