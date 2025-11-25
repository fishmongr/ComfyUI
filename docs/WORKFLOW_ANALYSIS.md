# Wan 2.2 i2v Workflow Analysis

## Your Current Workflow: `video_wan2_2_14B_i2v (2).json`

### ✅ Configuration Overview

**Two-Pass Setup:**
- **Pass 1**: High Noise Model + High Noise 4-step LoRA
  - KSampler: 4 steps, CFG 1.0, euler sampler
  - Start at step 0, end at step 2, return with noise enabled
  
- **Pass 2**: Low Noise Model + Low Noise 4-step LoRA  
  - KSampler: 4 steps, CFG 1.0, euler sampler
  - Start at step 2, end at step 4, disable noise

**Optimizations:**
- ✓ SageAttention3 enabled for both passes
- ✓ 4-step LoRAs loaded (high and low)
- ✓ ModelSamplingSD3 with shift values (5.0 for high, 6.0 for low)

**Configuration:**
- Resolution: 832x1216 (9:16 portrait)
- Frame count: 49 frames (~3s @ 16fps)
- Test image: sogni-photobooth-my-polar-bear-baby-raw.jpg

**Prompt (Positive):**
```
cinematic winter scene, gentle camera motion, soft natural lighting,
crisp snow highlights, realistic fur texture, calm atmosphere,
subtle breathing and micro-movements, detailed fabric,
high-resolution video diffusion, smooth temporal consistency,
pristine cold environment, warm expression, subtle sparkle in snow,
clean color balance, slow dolly-in, soft winter breeze,
gentle ambient sparkle, dreamy arctic atmosphere
```

**Prompt (Negative):**
```
distortion, blurry textures, morphing, inconsistent proportions,
extra limbs, duplicated features, stretched frames, flicker, jitter,
camera shake, warped shapes, low detail, oversharpen,
extreme motion blur, artifacting, color banding
```

### 🎯 Key Observations

1. **Advanced Two-Pass Strategy**: Your workflow uses KSamplerAdvanced with overlapping step ranges:
   - Pass 1: steps 0-2 (with noise)
   - Pass 2: steps 2-4 (without noise)
   - This creates a smooth transition between passes

2. **Very Low CFG**: CFG=1.0 for both passes
   - This is interesting! Standard workflows use 3.5-7.0
   - May contribute to faster generation
   - Need to test if this affects quality

3. **Shift Parameters**: Different for each model
   - High noise: shift=5.0
   - Low noise: shift=6.0
   - These control the noise schedule

4. **Has Both Modes**: Your workflow has both groups:
   - fp8_scaled + 4steps LoRA (enabled)
   - fp8_scaled only (disabled)

### 📊 Performance Notes from Workflow

According to the note in your workflow:
```
| Model            | Size     | VRAM Usage | 1st Gen    | 2nd Gen   |
|------------------|----------|------------|------------|-----------|
| fp8_scaled       | 640x640  | 84%        | ≈ 536s     | ≈ 513s    |
| fp8 + 4step LoRA | 640x640  | 83%        | ≈ 97s      | ≈ 71s     |
```

**Analysis**: On 4090D with 640x640, 4-step LoRA gives ~7x speedup!

Your reported benchmarks at 832x1216:
- 67-83s range (good performance)
- 114-126s range (degraded)

### 🔍 Testing Strategy

Based on your workflow, I'll create test variations:

1. **Baseline (your current config)**
   - 832x1216, 49 frames
   - CFG=1.0, 4 steps
   - SageAttention3 enabled

2. **5s duration test**
   - 832x1216, 81 frames (5s @ 16fps)
   - Same settings

3. **10s duration test**
   - 832x1216, 161 frames (10s @ 16fps)  
   - Same settings

4. **CFG comparison**
   - Test CFG 1.0 vs 3.5 vs 7.0
   - See if your low CFG=1.0 is optimal

### Next Steps

1. Copy your workflow as baseline
2. Create 5s and 10s variations
3. Test with TORCH_COMPILE=1 (was disabled)
4. Run automated benchmark suite
5. Compare results

Your workflow is well-optimized! The main question is whether TORCH_COMPILE=1 and different environment settings will restore the 67-80s performance consistently.

