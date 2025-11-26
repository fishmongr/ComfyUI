# CLIP Vision Integration Guide

## What is CLIP Vision?

CLIP Vision is a neural network that converts images into semantic embeddings - numerical representations that capture the **meaning** of an image, not just pixels.

### Why Use It?

**Without CLIP Vision:**
- Model sees: pixel patterns, colors, shapes
- Conditioning: VAE latent space only

**With CLIP Vision:**
- Model sees: concepts, objects, relationships  
- Conditioning: VAE latents + semantic understanding
- Result: Better consistency, especially for first+last frame interpolation

## Technical Details

### Model Sizes & VRAM

| Model | Size | VRAM (fp16) | VRAM (fp32) |
|-------|------|-------------|-------------|
| `clip_vit_base_patch32` | ~288 MB | ~346 MB | ~692 MB |
| `sigclip_vision_384` | ~400 MB | ~300 MB | ~500 MB |
| `clip_vision_g` | ~600 MB | ~350 MB | ~700 MB |

**Impact:** Only **~300-500 MB** additional VRAM - minimal compared to Wan 2.2's 14B model (~15-20 GB)

### How It Works

```
Input Image
    │
    ├──→ VAE Encode ──→ Latent features (pixel-level)
    │
    └──→ CLIP Vision ─→ Semantic embedding (concept-level)
                            │
                            ├──→ "person"
                            ├──→ "winter scene"
                            ├──→ "snowy background"
                            └──→ "warm clothing"
                            
Both signals → WanFirstLastFrameToVideo → Better conditioning
```

## Manual Integration (Current Method)

**Note:** CLIP Vision is not yet automated in `generate_wan22_video.py`. You need to edit the workflow manually.

### Step 1: Download CLIP Vision Model

Place in `models/clip_vision/`:

**Recommended:** SigLIP (newer, better quality)
```
models/clip_vision/sigclip_vision_384.safetensors
```

**Alternative:** CLIP-G (OpenAI)
```
models/clip_vision/clip_vision_g.safetensors
```

**Sources:**
- Hugging Face: https://huggingface.co/models?search=clip+vision
- ComfyUI Model Manager

### Step 2: Edit Workflow JSON

Add CLIP Vision nodes to `scripts/last_prompt_api_format_firstlast.json`:

#### 2.1 Add CLIPVisionLoader (node 120)

```json
"120": {
  "inputs": {
    "clip_name": "sigclip_vision_384.safetensors"
  },
  "class_type": "CLIPVisionLoader",
  "_meta": {
    "title": "Load CLIP Vision"
  }
}
```

#### 2.2 Add CLIPVisionEncode for First Frame (node 121)

```json
"121": {
  "inputs": {
    "clip_vision": ["120", 0],
    "image": ["97", 0],
    "crop": "center"
  },
  "class_type": "CLIPVisionEncode",
  "_meta": {
    "title": "CLIP Vision Encode (First)"
  }
}
```

#### 2.3 Add CLIPVisionEncode for Last Frame (node 122)

```json
"122": {
  "inputs": {
    "clip_vision": ["120", 0],
    "image": ["99", 0],
    "crop": "center"
  },
  "class_type": "CLIPVisionEncode",
  "_meta": {
    "title": "CLIP Vision Encode (Last)"
  }
}
```

#### 2.4 Update WanFirstLastFrameToVideo (node 98)

Add CLIP Vision inputs:

```json
"98": {
  "inputs": {
    "width": 832,
    "height": 1216,
    "length": 25,
    "batch_size": 1,
    "positive": ["93", 0],
    "negative": ["89", 0],
    "vae": ["90", 0],
    "start_image": ["97", 0],
    "end_image": ["99", 0],
    "clip_vision_start_image": ["121", 0],
    "clip_vision_end_image": ["122", 0]
  },
  "class_type": "WanFirstLastFrameToVideo",
  "_meta": {
    "title": "WanFirstLastFrameToVideo"
  }
}
```

### Step 3: Update Script (Optional)

Modify `update_api_prompt()` to conditionally add CLIP Vision nodes when `--clip-vision` flag is used.

## When to Use CLIP Vision

### ✅ Good Use Cases

1. **First + Last Frame Interpolation**
   - Helps model understand semantic relationship
   - Better consistency across the transition

2. **Complex Scenes**
   - Multiple subjects/objects
   - Detailed compositions
   - Specific concepts you want preserved

3. **Artistic/Stylized Content**
   - CLIP understands artistic styles
   - Better at maintaining aesthetic

### ⚠️ May Not Help

1. **Simple First-Frame-Only i2v**
   - VAE alone is usually sufficient
   - Minimal benefit for single-frame conditioning

2. **Abstract/Experimental**
   - CLIP trained on realistic images
   - May not understand abstract art as well

3. **VRAM-Constrained Systems**
   - If you're already maxed out on VRAM
   - The ~500 MB could push you over

## Performance Impact

### Memory
- **Additional VRAM:** ~300-500 MB
- **Percentage of total:** ~2-3% (on 16GB GPU)
- **Impact:** Negligible

### Speed
- **CLIP Vision encoding:** ~50-200ms per frame
- **For first+last:** ~100-400ms total
- **Percentage of generation:** < 1%
- **Impact:** Negligible

### Quality
- **Improvement:** Moderate to significant (depending on use case)
- **Best for:** First+last frame interpolation
- **Measurable:** Better semantic consistency

## Comparison: With vs Without

### Example: Face Expression Change

**Without CLIP Vision:**
```
First Frame: Neutral expression
Last Frame: Smiling

Result: Smooth motion, but face might morph oddly
        Eyes/mouth might blend unnaturally
```

**With CLIP Vision:**
```
First Frame: Neutral expression + CLIP("person, neutral face, looking forward")
Last Frame: Smiling + CLIP("person, smiling face, happy expression")

Result: Model understands "same person, changing expression"
        More natural facial feature transitions
        Better preservation of identity
```

## Future: Automated Integration

**Planned enhancement for `generate_wan22_video.py`:**

```bash
# Enable CLIP Vision automatically
python scripts/generate_wan22_video.py \
  input/first.jpg \
  --last-frame input/last.jpg \
  --clip-vision \
  --clip-model sigclip_vision_384
```

**Script will:**
1. Check if CLIP Vision model exists
2. Dynamically add nodes 120, 121, 122 to workflow
3. Connect to WanFirstLastFrameToVideo
4. Handle missing last frame gracefully

**Status:** Not yet implemented - manual workflow editing required

## Troubleshooting

### "CLIP Vision model not found"
- Check file is in `models/clip_vision/`
- Verify filename matches exactly in workflow

### No quality improvement visible
- CLIP Vision helps most with first+last frame
- Try with more challenging transitions
- Compare side-by-side with/without

### VRAM out of memory
- Remove CLIP Vision nodes from workflow
- CLIP Vision is optional enhancement
- VAE conditioning alone works fine

### Wrong CLIP Vision output
- Check `crop` parameter: "center" or "none"
- "center" is usually best for portraits
- "none" for full-frame content

## Advanced: Multiple CLIP Vision Models

You can use different CLIP models for different purposes:

**SigLIP (sigclip_vision_384):**
- Newer architecture
- Better semantic understanding
- Recommended for most uses

**CLIP-G (clip_vision_g):**
- OpenAI's model
- Widely used standard
- Good general purpose

**Experiment:** Try both and compare results!

## References

- [OpenAI CLIP Paper](https://arxiv.org/abs/2103.00020)
- [SigLIP Paper](https://arxiv.org/abs/2303.15343)
- ComfyUI CLIPVisionLoader documentation
- WanFirstLastFrameToVideo node source: `comfy_extras/nodes_wan.py`

## Summary

**CLIP Vision:**
- ✅ Adds semantic understanding (~500 MB VRAM)
- ✅ Best for first+last frame interpolation  
- ✅ Negligible performance impact
- ⚠️ Requires manual workflow editing (for now)
- ⚠️ Optional - not required for good results

**Bottom Line:** Worth trying if you're doing first+last frame interpolation and have the VRAM to spare!

