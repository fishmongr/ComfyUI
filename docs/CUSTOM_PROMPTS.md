# Custom Prompt Guide for Wan 2.2 i2v

## Overview

You can now customize both positive and negative prompts when generating videos using `generate_wan22_video.py`.

## Usage

### Basic Syntax

```bash
python scripts/generate_wan22_video.py <image_path> --positive "your prompt" --negative "things to avoid"
```

### Examples

**Short Positive Prompt:**
```bash
python scripts/generate_wan22_video.py input/photo.jpg \
  --positive "slow zoom in, soft lighting" \
  --negative "blurry, distorted"
```

**Detailed Cinematic Prompt:**
```bash
python scripts/generate_wan22_video.py input/photo.jpg \
  --frames 81 \
  --positive "cinematic slow motion, smooth camera pan left to right, golden hour lighting, soft focus background, natural color grading, professional cinematography, subtle depth of field" \
  --negative "blurry, distorted, warped shapes, flickering, jitter, camera shake, low detail, artifacting, color banding"
```

**Portrait with Motion:**
```bash
python scripts/generate_wan22_video.py input/portrait.jpg \
  --positive "gentle breathing, natural micro-movements, soft eye contact, realistic skin texture, ambient wind in hair, subtle smile" \
  --negative "morphing face, extra limbs, distorted features, unnatural motion blur"
```

**Nature Scene:**
```bash
python scripts/generate_wan22_video.py input/landscape.jpg \
  --positive "gentle breeze through trees, flowing water, natural lighting transitions, soft clouds moving, realistic vegetation movement" \
  --negative "flickering, harsh transitions, overprocessed, digital artifacts"
```

## Default Prompts

If you don't specify `--positive` or `--negative`, the script uses the prompts from your template workflow:

**Default Positive:**
```
cinematic winter scene, gentle camera motion, soft natural lighting,
crisp snow highlights, realistic fur texture, calm atmosphere,
subtle breathing and micro-movements, detailed fabric,
high-resolution video diffusion, smooth temporal consistency,
pristine cold environment, warm expression, subtle sparkle in snow,
clean color balance, slow dolly-in, soft winter breeze,
gentle ambient sparkle, dreamy arctic atmosphere
```

**Default Negative:**
```
distortion, blurry textures, morphing, inconsistent proportions,
extra limbs, duplicated features, stretched frames, flicker, jitter,
camera shake, warped shapes, low detail, oversharpen,
extreme motion blur, artifacting, color banding
```

## Prompt Engineering Tips

### Positive Prompt

**Good Keywords:**
- **Camera Motion**: slow zoom, dolly in/out, pan left/right, stationary, smooth tracking
- **Lighting**: soft lighting, golden hour, natural light, dramatic shadows, ambient glow
- **Motion**: gentle breathing, subtle micro-movements, flowing fabric, natural wind
- **Quality**: cinematic, high resolution, detailed textures, smooth temporal consistency
- **Atmosphere**: calm, dreamy, realistic, professional cinematography

**Structure:**
1. Camera movement description
2. Lighting/atmosphere
3. Subject-specific motion details
4. Quality/technical descriptors

### Negative Prompt

**Essential Keywords:**
- **Spatial Issues**: distortion, warped shapes, morphing, inconsistent proportions
- **Temporal Issues**: flickering, jitter, frame stutter, jerky motion
- **Quality Issues**: blurry, low detail, artifacting, color banding, over-sharpened
- **Artifacts**: extra limbs, duplicated features, unnatural deformations

## Combining with Interpolation

For best results with FILM interpolation:

```bash
python scripts/generate_wan22_video.py input/photo.jpg \
  --frames 81 \
  --positive "smooth slow motion, fluid movement, natural temporal flow" \
  --negative "jerky motion, frame stutter, temporal artifacts" \
  --interpolate film \
  --crf 18
```

The prompt keywords like "smooth temporal consistency" and "fluid movement" help the model generate frames that interpolate better.

## Technical Details

### Node Mapping

- `--positive` updates **Node 93** (CLIP Text Encode - Positive Prompt)
- `--negative` updates **Node 89** (CLIP Text Encode - Negative Prompt)

### Character Limits

- No hard character limits, but keep prompts focused
- Recommended: 200-500 characters for positive, 100-200 for negative
- Very long prompts may dilute effectiveness

### Prompt Weighting

Wan 2.2 i2v uses CFG=1.0, so prompt influence is balanced. Unlike some models:
- You don't need emphasis syntax like `(word:1.5)`
- Clear, descriptive language works best
- Order matters slightly - put most important concepts first

## Workflow Integration

These prompts are injected into the workflow at queue time and override the template defaults. Your original template file remains unchanged.

## Troubleshooting

**Issue**: Prompt ignored, using defaults
- **Solution**: Make sure you're using `--positive` and `--negative` (not `-p` or other shortcuts)

**Issue**: ComfyUI rejects prompt
- **Solution**: Check for special characters that need escaping in your shell (quotes, backslashes)

**Issue**: Results don't match prompt
- **Solution**: Try more specific keywords, avoid abstract concepts, use clear camera/motion descriptors

## Examples by Use Case

### Product Video
```bash
--positive "360 degree rotation, studio lighting, clean background, professional showcase, smooth rotation"
--negative "blurry, poor lighting, background clutter, jerky movement"
```

### Portrait Animation
```bash
--positive "natural breathing, gentle head turn, soft eye blink, realistic skin movement, ambient lighting"
--negative "morphing face, unnatural expressions, distorted features, flickering"
```

### Landscape Scene
```bash
--positive "subtle cloud movement, gentle camera drift, natural lighting shift, smooth panorama"
--negative "harsh cuts, flickering sky, warped horizon, artificial motion"
```

### Action/Dynamic
```bash
--positive "fast camera follow, dynamic motion blur, energetic movement, smooth tracking shot"
--negative "frame stutter, choppy motion, excessive blur, shaky camera"
```

