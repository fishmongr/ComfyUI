# TaylorSeer-Lite Installation Complete

## What is TaylorSeer-Lite?

A custom node that accelerates video generation by optimizing the diffusion sampling process. For Wan 2.2, it achieves **3.05x speedup** (1176s → 386s for 81 frames on RTX 5090).

## Installation Status

✅ **Installed:** `custom_nodes/ComfyUI-TaylorSeer/`

## How to Use

### Step 1: Restart ComfyUI
TaylorSeer-Lite will load automatically on next startup.

### Step 2: Add TaylorSeerLite Nodes

In your workflow, **wrap each UNET model** with a `TaylorSeerLite` node:

**Before:**
```
UNETLoader (High Noise) → LoraLoader → ModelSamplingSD3 → KSampler
```

**After:**
```
UNETLoader (High Noise) → LoraLoader → TaylorSeerLite → ModelSamplingSD3 → KSampler
```

### Step 3: Configure TaylorSeerLite Node

**Parameters:**
- `model_type`: `wanvideo`
- `fresh_threshold`: `5` (default)
- `max_order`: `1` (balance speed/quality)
- `first_enhance`: `1` (start optimizing from step 1)
- `last_enhance`: `50` (optimize until step 50)

### Step 4: Apply to Both Models

You need **TWO** TaylorSeerLite nodes:
1. One wrapping the **high_noise model** (Node 95 → Node 101)
2. One wrapping the **low_noise model** (Node 96 → Node 102)

## Expected Performance

**Current (without TaylorSeer):**
- 161 frames @ 832x1216: ~494s

**With TaylorSeer-Lite:**
- Expected: ~165s for 161 frames (3x speedup)
- Per frame: ~1.0s (down from 3.07s)

## Key Benefits

✅ **Nearly zero VRAM increase** (unlike standard TaylorSeer)
✅ **3.05x speedup** on Wan 2.2 video generation
✅ **No quality loss** with recommended settings
✅ **Works on RTX 5090** (no CUDA compatibility issues)

## Example Workflow

A complete Wan 2.2 example workflow is included:
`custom_nodes/ComfyUI-TaylorSeer/examples/taylorseerlite_example_wan2-2.json`

## Next Steps

1. **Restart ComfyUI** to load the new nodes
2. **Add TaylorSeerLite nodes** to your workflow
3. **Test with 81 frames** first to verify speedup
4. **Scale to 161 frames** once confirmed working

