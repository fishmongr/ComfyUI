# Updated Filename Guide

## Final Output Only

The two-pass workflow (high_noise → low_noise) is **internal processing**. Only the final result is saved as an MP4 file.

## Filename Pattern

```
{source-name}_%width%x%height%_{frames}f_{duration}_{settings}_%year%%month%%day%_%hour%%minute%%second%
```

### Example Output:
```
polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_143045_00001_.mp4
```

### What Each Part Means:
- `polar-bear` - Source image name (auto-extracted from input)
- `832x1216` - Video resolution (auto from workflow)
- `25f` - Frame count
- `1.6s` - Duration in seconds (25 ÷ 16fps)
- `4step_nosage` - Settings used (see below)
- `20251123_143045` - Timestamp
- `00001` - Auto counter

## Settings Abbreviations

| Setting | Code | When to Use |
|---------|------|-------------|
| 4-Step LoRA enabled, no SageAttention | `4step_nosage` | **Default/Current** |
| 4-Step LoRA enabled, with SageAttention | `4step_sage3` | If we fix SageAttention |
| No LoRA, no SageAttention | `20step_nosage` | For quality comparison tests |
| With frame interpolation (RIFE) | Add `_rife_32fps` | After interpolation |
| With frame interpolation (FILM) | Add `_film_32fps` | After interpolation |

## Duration Reference

| Frames | Duration @ 16fps | After RIFE (32fps) |
|--------|------------------|--------------------|
| 17 | 1.1s | 2.1s (34f) |
| 25 | 1.6s | 3.1s (50f) |
| 33 | 2.1s | 4.1s (66f) |
| 49 | 3.1s | 6.1s (98f) |
| 65 | 4.1s | 8.1s (130f) |
| 81 | 5.1s | 10.1s (162f) |
| 161 | 10.1s | 20.1s (322f) |

## Using the Generation Script

### Basic Usage
```bash
# Default: 25 frames, 832x1216
python scripts/generate_wan22_video.py input/my-polar-bear-image.jpg

# Output: my-polar-bear-image_832x1216_25f_1.6s_4step_nosage_20251123_143045_00001_.mp4
```

### Custom Frame Count
```bash
# 49 frames (3 second video)
python scripts/generate_wan22_video.py input/my-image.jpg --frames 49

# 81 frames (5 second video)
python scripts/generate_wan22_video.py input/my-image.jpg --frames 81
```

### Custom Resolution
```bash
# Square 1024x1024
python scripts/generate_wan22_video.py input/my-image.jpg --width 1024 --height 1024 --frames 81
```

### Custom Settings Tag
```bash
# If you enable SageAttention or change other settings
python scripts/generate_wan22_video.py input/my-image.jpg --settings "4step_sage3"
python scripts/generate_wan22_video.py input/my-image.jpg --settings "20step_nosage"
```

### Full Example
```bash
python scripts/generate_wan22_video.py \
    input/sogni-photobooth-my-polar-bear-baby-raw.jpg \
    --frames 49 \
    --width 832 \
    --height 1216 \
    --settings "4step_nosage" \
    --timeout 600

# Output: my-polar-bear-baby_832x1216_49f_3.1s_4step_nosage_20251123_143045_00001_.mp4
```

## Script Features

✅ **Auto-extracts source name** from image path  
✅ **Calculates duration** automatically  
✅ **Updates workflow** with correct settings  
✅ **Monitors progress** in real-time  
✅ **Shows completion status** and output path  
✅ **Handles errors** gracefully  
✅ **Timeout protection** (default 600s)

## What the Script Does

1. **Loads** your source image
2. **Extracts** clean source name (removes "sogni-photobooth-", "-raw", etc.)
3. **Updates** the workflow JSON with:
   - Image path
   - Frame count
   - Resolution
   - Dynamic filename pattern
4. **Submits** to ComfyUI API
5. **Monitors** queue and progress
6. **Reports** when complete with output path

## Example Output

```
======================================================================
Wan 2.2 i2v Video Generation
======================================================================
Source Image:  input/sogni-photobooth-my-polar-bear-baby-raw.jpg
Source Name:   my-polar-bear-baby
Resolution:    832x1216
Frames:        25 (1.6s @ 16fps)
Settings:      4step_nosage
Workflow:      user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json
ComfyUI URL:   http://localhost:8188
======================================================================

📝 Loading workflow...
🚀 Submitting to ComfyUI...
✓ Prompt queued with ID: 12345678-1234-1234-1234-123456789abc

⏳ Waiting for generation to complete (timeout: 600s)...
🔄 Processing...
✅ Generation completed!

✅ Video saved: output/video/my-polar-bear-baby_832x1216_25f_1.6s_4step_nosage_20251123_143045_00001_.mp4
   File size: 12.34 MB
```

## Requirements

- ComfyUI running at `http://localhost:8188` (default)
- Image must be in ComfyUI's input folder or accessible path
- Workflow JSON must exist at specified path

---
**Last Updated**: 2025-11-23  
**Script**: `scripts/generate_wan22_video.py`
