# TaylorSeer Workflow Ready!

## ✅ Created: `video_wan2_2_14B_i2v_TAYLORSEER.json`

### What Was Added

**Two TaylorSeerLite nodes** inserted into the model chain:

1. **Node 121: TaylorSeerLite (High Noise)**
   - Position: Between LoRA 101 and ModelSampling 104
   - Settings: `wanvideo`, threshold=5, max_order=1, first_enhance=1, last_enhance=50

2. **Node 122: TaylorSeerLite (Low Noise)**
   - Position: Between LoRA 102 and ModelSampling 103
   - Settings: `wanvideo`, threshold=5, max_order=1, first_enhance=1, last_enhance=50

### New Model Flow

```
High Noise Pass:
UNET 95 → LoRA 101 → [TaylorSeer 121] → ModelSampling 104 → Sage3 117 → KSampler 86

Low Noise Pass:
UNET 96 → LoRA 102 → [TaylorSeer 122] → ModelSampling 103 → Sage3 118 → KSampler 85
```

## Expected Performance

### Current (NO_UNLOAD workflow):
- **161 frames @ 832x1216:** ~494 seconds
- **Per frame:** 3.07 seconds

### With TaylorSeer-Lite:
- **161 frames @ 832x1216:** ~165 seconds (estimated)
- **Per frame:** ~1.0 second
- **Speedup:** 3x faster

## Next Steps

1. **Restart ComfyUI** to load TaylorSeer nodes
2. **Load the workflow:** `video_wan2_2_14B_i2v_TAYLORSEER.json`
3. **Test with 81 frames first** to verify it works
4. **Scale to 161 frames** once confirmed

## Settings Explanation

- `model_type: wanvideo` - Optimized for video generation models
- `fresh_threshold: 5` - How often to recalculate cache
- `max_order: 1` - Balance between speed and quality (1 is recommended)
- `first_enhance: 1` - Start optimization from first sampling step
- `last_enhance: 50` - Continue optimization through all steps

## Troubleshooting

If nodes show as "missing" after restart:
- TaylorSeer custom node didn't load
- Check `custom_nodes/ComfyUI-TaylorSeer/` exists
- Check ComfyUI console for errors during startup

## Benchmarks Reference

Published benchmark (RTX 5090):
- **81 frames WITHOUT TaylorSeer:** 1176 seconds (19.6 minutes)
- **81 frames WITH TaylorSeer:** 386 seconds (6.4 minutes)
- **Speedup:** 3.05x

Your workflow is already optimized with 4-step LoRA, so actual speedup might be closer to 2-2.5x, but still significant!

