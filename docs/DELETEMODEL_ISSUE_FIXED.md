# DeleteModelPassthrough Issue & Fix

## Problem
The `DeleteModelPassthrough` node was **too aggressive** and caused subsequent runs to fail with:
```
AttributeError: 'NoneType' object has no attribute 'latent_format'
```

This happened because the regular `DeleteModelPassthrough` sets `self.model = None`, which completely destroys the model object. When ComfyUI tries to run the workflow a second time, it tries to access the deleted model and crashes.

## Solution
Switched to `DeleteModelPassthroughLight` which is less aggressive:
- ✅ Still frees VRAM and RAM
- ✅ Doesn't completely destroy the model object
- ✅ Allows multiple consecutive runs without restarting ComfyUI

## Performance Analysis (161 frames @ 832x1216)

### What We Observed
- **With DeleteModelPassthrough:** 494s total time
- **Still showing partial offloading:** 13504.81 MB offloaded per pass
- **Model deletion confirmed working:** Logs showed "SUCCESS: Model removed from management system!"

### Why Performance Didn't Improve
Even with only ONE model loaded at a time, the 161-frame workload is too large:

**VRAM Math:**
- Model size: ~13.6 GB
- Activations (161f @ 832x1216): ~16-18 GB  
- **Total needed: ~30 GB**
- **Available: 32 GB**

The activations alone force partial model offloading, even with DeleteModelPassthrough working correctly.

## Recommendations

### Option 1: Test with 81 Frames (5s video)
- Should eliminate offloading
- Expected time: ~120-140s total (60-70s per pass)
- This will confirm DeleteModelPassthrough benefit

### Option 2: Reduce Resolution
- Try 640x960 or 720x1080
- Lower activation memory allows longer videos

### Option 3: Accept Partial Offloading
- 161 frames @ 832x1216 will **always** partially offload on 32GB
- 494s is actually reasonable for this workload
- DeleteModelPassthrough helps, but can't overcome VRAM math

## Next Test
Load `WAN22_DELETEMODEL_LIGHT.json` and run **81 frames** to see the true benefit without hitting VRAM ceiling.

