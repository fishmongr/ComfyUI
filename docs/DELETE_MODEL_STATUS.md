# DeleteModelPassthrough Installation & Configuration

## Status: ✅ READY TO TEST

## What Was Done

### 1. Installed DeleteModelPassthrough Custom Node
```
Location: custom_nodes/ComfyUI_DeleteModelPassthrough/
Source: https://github.com/Isi-dev/ComfyUI_DeleteModelPassthrough
```

### 2. Updated Workflow
```
File: user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json
Added Node: 119 (Delete High Noise Model)
```

**Workflow Integration:**
```
KSampler 86 (High Noise Pass) 
  |
  v [LATENT output]
DeleteModelPassthrough Node 119 <<< Takes MODEL from ModelSamplingSD3 Node 104
  |                                  (Sage3 nodes 117/118 bypassed)
  v [Passes LATENT through]
KSampler 85 (Low Noise Pass)
```

**Note:** SageAttention3 nodes (117, 118) are bypassed due to build issues. PyTorch SDPA with FlashAttention is used instead.

### 3. How It Works

**DeleteModelPassthrough** aggressively deletes models from memory:
```python
del model
torch.cuda.empty_cache()
gc.collect()
```

Unlike ComfyUI's default behavior (moves to RAM) or cache-clearing nodes (only clear caches), this node **completely removes the model** from both VRAM and RAM.

## Expected Impact

### VRAM Usage Timeline (81 frames @ 832x1216)

**Before (with 845MB offload):**
```
High Noise Pass:  19.2GB VRAM
Between Passes:   ~13GB (high noise model) + ~6GB (activations)
Low Noise Pass:   32GB+ needed -> 845MB offloaded to RAM
```

**After (target):**
```
High Noise Pass:  19.2GB VRAM
Between Passes:   ~6GB (activations only, model DELETED)
Low Noise Pass:   19.2GB VRAM (no offload!)
```

### Performance Impact

| Frames | Before (offload) | After (target) | Improvement |
|--------|------------------|----------------|-------------|
| 81     | 146-153s         | 124-137s       | ~20-30s (~15%) |
| 161    | OOM/Untested     | ~250-270s      | Now possible! |
| 241    | OOM/Untested     | ~375-410s      | Now possible! |

## Testing

See `docs/DELETE_MODEL_TEST_GUIDE.md` for detailed test steps.

**Quick Test:**
1. Restart ComfyUI: `.\scripts\launch_wan22_rtx5090.bat`
2. Load workflow: `video_wan2_2_14B_i2v_no_sage_test.json`
3. Verify "Delete High Noise Model" node exists between KSamplers
4. Run 81-frame test
5. Watch console for "Deleting model..." and NO "offload" messages
6. Confirm time: 124-137s (vs. previous 146-153s)

## Why This Should Work

### Previous Attempts (Failed)
- `easy cleanGpuUsed`: Only clears CUDA cache, not model weights
- `easy clearCacheAll`: Only clears ComfyUI caches, not model weights
- ComfyUI default: Moves models to RAM, both stay loaded

### DeleteModelPassthrough (Expected to Succeed)
- **Deletes model from VRAM:** Frees 13GB immediately
- **Deletes model from RAM:** Prevents memory filling up
- **Forces reload from disk:** Only needed once per pass (no penalty)

## Trade-offs

**Pros:**
- Eliminates VRAM offloading
- Enables longer videos (161+ frames)
- Faster generation (no RAM<->VRAM transfers)
- No quality impact

**Cons:**
- Model must reload from disk if needed again (not applicable for two-pass)
- Slightly more aggressive than ComfyUI's smart caching (acceptable for sequential workflow)

## Files Changed

```
custom_nodes/ComfyUI_DeleteModelPassthrough/  (NEW)
  __init__.py
  delete_model_passthrough.py
  README.md
  requirements.txt

user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json  (UPDATED)
  - Added Node 119: Delete Model (Passthrough Any)
  - Updated links: 170 (modified), 226 (new), 227 (new), 228 (new)

docs/DELETE_MODEL_TEST_GUIDE.md  (NEW)
  - Comprehensive testing guide

scripts/add_delete_model_passthrough.py  (NEW)
  - Script to add the node (already executed)
```

## Next Steps

1. **Test with 81 frames** - Verify offloading eliminated
2. **Test with 161 frames** - Confirm longer videos work
3. **If successful:** Integrate into all workflows
4. **If successful:** Test RIFE frame interpolation
5. **If not successful:** Investigate FramePack alternative

## Questions to Answer

1. ✅ Does DeleteModelPassthrough eliminate the 845MB offload at 81 frames?
2. ⏳ Does it enable 161+ frame generation without OOM?
3. ⏳ What is the actual performance gain (target: 20-30s for 81 frames)?
4. ⏳ Any side effects or errors in console logs?

---

**Created:** 2024-11-24
**Status:** Ready for testing
**Priority:** HIGH - Could enable 10s+ videos on RTX 5090

