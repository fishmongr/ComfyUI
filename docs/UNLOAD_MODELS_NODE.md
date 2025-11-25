# Unload Models Node - VRAM Management for Two-Pass Workflows

## Problem Identified

**Issue:** In your two-pass workflow (high_noise → low_noise), ComfyUI keeps BOTH models loaded in VRAM simultaneously (~27GB), causing offloading to RAM at 61+ frames.

**Expected Behavior:** The first model should unload after Pass 1, freeing ~13.6GB for the second model.

**Actual Behavior:** Both models stay loaded because ComfyUI sees sequential nodes and assumes they both need to be ready.

## Solution: UnloadModels Node

### Installation

The custom node is already installed at:
```
custom_nodes/unload_models_node.py
```

Restart ComfyUI to load the node.

### How to Use

1. **In ComfyUI UI:**
   - After your first KSampler (high_noise pass)
   - Before your second KSampler (low_noise pass)
   - Add node: Right-click → Add Node → model_management → **Unload All Models (Free VRAM)**

2. **Connect it in the workflow:**

```
[High Noise KSampler] → [OUTPUT: LATENT]
         ↓
[UnloadModels Node] ← (connect OUTPUT from KSampler to "anything" input)
         ↓
[Low Noise KSampler] ← (connect LATENT through UnloadModels)
```

### What It Does

When the workflow reaches this node:
1. Unloads all currently loaded models from VRAM
2. Calls PyTorch's `torch.cuda.empty_cache()` to free memory
3. Passes through the latent/image data unchanged
4. Next model load gets clean, defragmented VRAM

### Expected Results

**Before (61 frame limit):**
- Pass 1: High noise model loaded fully (13.6GB)
- Pass 2: Low noise model tries to load → **both in VRAM** (27GB) → offloading starts
- Performance: 146-160s for 81 frames

**After (with UnloadModels):**
- Pass 1: High noise model loaded fully (13.6GB)
- **[UnloadModels Node]** → Free 13.6GB
- Pass 2: Low noise model loaded fully (13.6GB) → clean VRAM
- Performance: **Target 120-130s** for 81 frames (no offloading)

## Testing Steps

1. Restart ComfyUI:
```batch
.\scripts\launch_wan22_rtx5090.bat
```

2. Open your workflow:
```
user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json
```

3. Add the UnloadModels node between passes

4. Test 81 frames (should NOT offload)

5. Test 161 frames (should work much better)

## Alternative: Modify Workflow JSON Directly

If you want to script this, I can add the UnloadModels node to your workflow JSON programmatically.

## Next Steps

Would you like me to:
1. **Add the UnloadModels node to your workflow JSON automatically?** ✅ (Recommended - quick test)
2. **Wait for you to add it manually in the UI?** (Better for learning the node)
3. **Test if there's already a built-in way to do this?** (Research alternative)

**Recommendation:** Let me add it to your workflow JSON so you can test immediately. If it works, you'll see dramatic improvement at 81+ frames!

