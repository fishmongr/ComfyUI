# WanFirstLastFrameToVideo Guide

## Overview

The updated `generate_wan22_video.py` script now uses the `WanFirstLastFrameToVideo` node, which provides flexible frame conditioning options:

1. **First frame only** (traditional i2v) - animate from a single image
2. **First + Last frames** - interpolate between two images
3. **Optional CLIP Vision** - enhanced semantic understanding (advanced)

## Quick Start

### First Frame Only (Traditional i2v)

```bash
python scripts/generate_wan22_video.py input/my-image.jpg
```

This works exactly like before - generates video from a single starting image.

### Last Frame Only (Reverse i2v) - NEW!

```bash
python scripts/generate_wan22_video.py input/target-frame.jpg --last-only
```

Generates a video that **leads TO** the target frame. The model creates the preceding frames to reach this final state.

### First + Last Frame Interpolation

```bash
python scripts/generate_wan22_video.py input/first-frame.jpg --last-frame input/last-frame.jpg
```

The model will:
- Start with the first frame
- End with the last frame  
- Smoothly interpolate motion/changes between them

### Use Cases for First+Last Frame

**Camera movements:**
```bash
# Zoom in effect
python scripts/generate_wan22_video.py input/wide-shot.jpg --last-frame input/close-up.jpg
```

**Subject transformations:**
```bash
# Expression change
python scripts/generate_wan22_video.py input/neutral-face.jpg --last-frame input/smiling-face.jpg
```

**Scene transitions:**
```bash
# Day to night
python scripts/generate_wan22_video.py input/daytime.jpg --last-frame input/nighttime.jpg
```

### Use Cases for Last Frame Only

**Reveal effects:**
```bash
# Generate video revealing a final product
python scripts/generate_wan22_video.py input/finished-art.jpg --last-only
```

**Approach animations:**
```bash
# Object coming into frame
python scripts/generate_wan22_video.py input/object-centered.jpg --last-only
```

**Anticipation builds:**
```bash
# Build up to a dramatic moment
python scripts/generate_wan22_video.py input/dramatic-pose.jpg --last-only
```

## Complete Usage Examples

### Example 1: Basic First+Last

```bash
python scripts/generate_wan22_video.py \
  input/start.jpg \
  --last-frame input/end.jpg \
  --frames 49
```

### Example 2: With Custom Prompts

```bash
python scripts/generate_wan22_video.py \
  input/start.jpg \
  --last-frame input/end.jpg \
  --frames 81 \
  --positive "smooth camera pan, cinematic motion" \
  --negative "jitter, blur, distortion"
```

### Example 3: With FILM Interpolation

```bash
python scripts/generate_wan22_video.py \
  input/start.jpg \
  --last-frame input/end.jpg \
  --frames 49 \
  --interpolate film \
  --crf 18
```

This will:
1. Generate 49 frames at 16fps (3s video)
2. Interpolate to 32fps using FILM (~6s final video)

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `image_path` | Path to first frame (or last if --last-only) | - |
| `--last-frame` | Path to last frame (for first+last mode) | None |
| `--last-only` | Use image_path as last frame only | False |
| `--frames` | Number of frames to generate | 25 |
| `--width` | Video width | 832 |
| `--height` | Video height | 1216 |
| `--positive` | Positive prompt | Template default |
| `--negative` | Negative prompt | Template default |
| `--settings` | Settings tag for filename | 4step_nosage |
| `--interpolate` | FILM interpolation (film/none) | none |
| `--crf` | Quality for interpolated video | 18 |
| `--timeout` | Generation timeout (seconds) | Auto |
| `--url` | ComfyUI URL | http://localhost:8188 |

## Frame Recommendations

**Resolution: 832x1216 (9:16 portrait)**

| Duration | Frames | Use Case |
|----------|--------|----------|
| 1.6s | 25 | Quick motion test |
| 3.0s | 49 | Short scene |
| 5.0s | 81 | Standard video |
| 10.0s | 161 | Long transition |

**Formula:** `frames = (duration_seconds * 16) + 1`

## Tips for First+Last Frame

### 1. Frame Similarity
- **Best results:** Similar composition, different details
- **Avoid:** Drastically different scenes/angles

### 2. Consistent Elements
- Keep the same subject in frame
- Maintain similar lighting direction
- Preserve overall composition

### 3. Prompt Strategy
When using first+last, describe the **motion/transformation**:

```bash
--positive "smooth transition, gradual transformation, seamless motion"
--negative "sudden changes, teleporting, morphing artifacts"
```

### 4. Frame Count
- **Shorter videos (25-49 frames):** More abrupt transitions
- **Longer videos (81-161 frames):** Smoother, more natural interpolation

## Workflow Template

The script uses: `scripts/last_prompt_api_format_firstlast.json`

**Key changes from original:**
- Node 98: `WanImageToVideo` → `WanFirstLastFrameToVideo`
- Node 97: First frame image loader
- Node 99: Last frame image loader (created dynamically when needed)

## Advanced: CLIP Vision Support

**Status:** Available but not yet integrated in script (manual workflow editing required)

CLIP Vision adds semantic understanding to frame conditioning. See `docs/CLIP_VISION_GUIDE.md` for details.

**Benefits:**
- Better understanding of image content
- Improved consistency in first+last interpolation  
- Only ~300-500 MB additional VRAM

**To enable:** Edit workflow manually to add CLIPVisionLoader and CLIPVisionEncode nodes.

## Troubleshooting

### "Last frame image not found"
- Check file path is correct
- Use absolute or relative path from project root

### Video doesn't reach last frame
- Increase frame count (more frames = better interpolation)
- Check both images are similar enough

### Artifacts between frames
- Reduce motion/change between first and last
- Adjust negative prompt to prevent morphing
- Use more frames for smoother transition

### VRAM out of memory
- CLIP Vision is optional - not currently enabled
- Reduce resolution if needed
- See main optimization docs

## Output Files

Files are saved to `output/video/` with naming pattern:

```
{source}_{width}x{height}_{frames}f_{duration}_{mode}_{settings}_{timestamp}.mp4
```

Where `{mode}` is:
- `first` - First frame only
- `last_only` - Last frame only (reverse i2v)
- `first_last` - First + Last frame interpolation

**Example:**
```
output/video/my-scene_832x1216_49f_3.0s_first_last_4step_nosage_20250125_143022.mp4
```

## Next Steps

1. Try basic first-frame-only generation
2. Experiment with first+last frame pairs
3. Adjust frame count for desired smoothness
4. Combine with FILM interpolation for 32fps output

For CLIP Vision integration, see `docs/CLIP_VISION_GUIDE.md` (coming soon).

