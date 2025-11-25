# Wan 2.2 i2v Two-Pass Workflow Guide

## Overview

Wan 2.2 i2v uses a two-pass workflow where both the high_noise and low_noise models are applied sequentially to produce the highest quality output.

## Available Nodes

From `comfy_extras/nodes_wan.py`:
- `Wan22FunControlToVideo` - Main node for Wan 2.2 i2v generation
- `Wan22ImageToVideoLatent` - Alternative latent-based approach

## Two-Pass Workflow Structure

### Pass 1: Initial Generation
```
Input Image → Load Model (high_noise or low_noise) 
           → Load LoRA (matching noise level)
           → Wan22FunControlToVideo node
           → KSampler (with 4-step LoRA: only 4 steps!)
           → VAE Decode
           → Intermediate Video Frames
```

### Pass 2: Refinement
```
Pass 1 Output → Load Model (opposite noise level)
             → Load LoRA (matching noise level)
             → Wan22FunControlToVideo node
             → KSampler (4 steps)
             → VAE Decode
             → Final Video Output
```

## Model and LoRA Paths

**Models** (in `models/diffusion_models/`):
- `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors`
- `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors`

**LoRAs** (in `models/loras/`):
- `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors`
- `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors`

**VAE** (in `models/vae/`):
- `wan_2.1_vae.safetensors`

**Text Encoder** (in `models/text_encoders/`):
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`

## Critical Parameters

### Resolution (832x1216 - Portrait)
- Width: 832
- Height: 1216  
- This is 9:16 aspect ratio, optimal for portrait videos

### Frame Count
- 5 seconds @ 16fps = 81 frames
- 10 seconds @ 16fps = 161 frames
- Formula: `frames = (duration_seconds * 16) + 1`

### Sampler Settings with 4-Step LoRA
- **Steps**: 4 (LoRA enables high quality with only 4 steps!)
- **CFG Scale**: 7.0 (typical)
- **Sampler**: euler or dpmpp_2m
- **Scheduler**: normal or karras

## Pass Order Testing

Need to test both orders to determine which produces better results:

**Order A: High → Low**
1. First pass: high_noise model + high_noise LoRA
2. Second pass: low_noise model + low_noise LoRA

**Order B: Low → High**
1. First pass: low_noise model + low_noise LoRA
2. Second pass: high_noise model + high_noise LoRA

## Performance Targets

With 4-step LoRA enabled:
- **Per pass**: 67-80 seconds
- **Two-pass total**: 134-160 seconds
- **Target resolution**: 832x1216
- **Target duration**: 5 seconds (81 frames)

## Building the Workflow in ComfyUI

### Step-by-Step (High → Low Order):

1. **Load Models and LoRAs**
   - Add "Load Diffusion Model" node → Select high_noise model
   - Add "Load LoRA" node → Select high_noise 4-step LoRA
   - Add "Load VAE" node → Select wan_2.1_vae

2. **Setup Text Encoding**
   - Add "CLIP Text Encode (Prompt)" nodes for positive and negative prompts
   - Connect to loaded model

3. **Pass 1: High Noise Generation**
   - Add "Load Image" node → Your test image
   - Add "Wan22FunControlToVideo" node:
     - Width: 832
     - Height: 1216
     - Length: 81 (for 5s)
     - Connect start_image to loaded image
     - Connect VAE
     - Connect conditioning
   
   - Add "KSampler" node:
     - Steps: 4 (with LoRA)
     - CFG: 7.0
     - Sampler: euler
     - Connect latent from Wan22FunControlToVideo
     - Connect model from LoRA
   
   - Add "VAE Decode (Video)" node
     - Connect samples from KSampler
     - Connect VAE

4. **Pass 2: Low Noise Refinement**
   - Add "Load Diffusion Model" → Select low_noise model
   - Add "Load LoRA" → Select low_noise 4-step LoRA
   
   - Add another "Wan22FunControlToVideo" node:
     - Same settings as Pass 1
     - Connect start_image to Pass 1 output video
   
   - Add "KSampler" (4 steps again)
   - Add "VAE Decode (Video)"

5. **Save Output**
   - Add "VHS_VideoCombine" or "Save Video" node
   - Connect to Pass 2 output
   - Set fps: 16

6. **Export Workflow**
   - Save as: `workflows/wan22_i2v_baseline_high_to_low_5s.json`

## Testing Notes

- Always use matching model and LoRA (high with high, low with low)
- 4-step LoRA is critical for performance - don't increase steps!
- Monitor VRAM usage during each pass
- First pass typically uses more VRAM than second
- If OOM occurs, may need to unload first model before loading second

## Expected Behavior

- Pass 1 generates initial video with good motion
- Pass 2 refines details and improves temporal consistency
- Total quality should be superior to single-pass
- Performance: ~70s + ~70s = ~140s for 5s video

## Troubleshooting

**OOM Error on Pass 2:**
- Manually unload Pass 1 model before loading Pass 2
- Reduce batch size to 1
- Consider --reserve-vram flag

**Slow Performance (>85s per pass):**
- Verify 4-step LoRA is loaded
- Check KSampler steps is set to 4, not higher
- Verify optimized launch flags are used
- Check TORCH_COMPILE=1 in environment

**Poor Quality:**
- Ensure both passes are using matching LoRAs
- Verify CFG scale isn't too high (7.0 is good)
- Check that second pass is using first pass output as input

