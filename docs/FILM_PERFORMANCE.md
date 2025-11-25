# FILM Interpolation Performance Characteristics

## Summary

FILM interpolation is **CPU/GPU intensive** and processes **frame-by-frame sequentially**. For long videos (>100 frames), expect **significant processing time**.

## Performance Benchmarks

### Measured Performance (832x1216 resolution)

| Frames | Frame Pairs | Time     | Per Pair | Total Pipeline |
|--------|-------------|----------|----------|----------------|
| 25     | 24          | ~19s     | 0.79s    | ~20s           |
| 161    | 160         | ~2-3min  | 0.75-1s  | ~2.5-3.5min    |

### Time Breakdown

For 161 frames:
1. **Extract PNGs**: ~5-10s
2. **Load frames to tensor**: ~5s
3. **FILM VFI processing**: ~2-3min (160 frame pairs × 0.75-1s each)
4. **Save interpolated PNGs**: ~30-60s
5. **Encode to video**: ~10-15s

**Total**: ~3-5 minutes for 161 frames

## Why Is It Slow?

### Sequential Processing
FILM processes frame pairs one at a time:
```python
for frame_itr in range(len(frames) - 1):
    frame_0 = frames[frame_itr]
    frame_1 = frames[frame_itr+1]
    interpolated = model(frame_0, frame_1)  # ~0.75-1s per pair
```

### Model Complexity
- FILM uses a **deep neural network** with recursive refinement
- Each frame pair requires multiple GPU forward passes
- Model is optimized for quality, not speed

### Resolution Impact
Higher resolutions take longer:
- 512x768: ~0.4s per pair
- 832x1216: ~0.75s per pair
- 1024x1536: ~1.2s per pair

## Progress Indicators

During processing, watch for these messages:

```
[INFO] Running FILM VFI with multiplier=2...
[INFO] This will process 160 frame pairs...
[INFO] Estimated time: ~80-160 seconds
[INFO] Processing 161 frames, cache clearing every 30 frames

Comfy-VFI: Clearing cache... Done cache clearing  <-- Progress indicator
Comfy-VFI: Clearing cache... Done cache clearing  <-- Shows it's working
Comfy-VFI: Clearing cache... Done cache clearing
Comfy-VFI: Final clearing cache... Done cache clearing

[INFO] FILM VFI completed in 150.2s (0.94s per frame pair)
```

**Key**: If you see "Clearing cache" messages every 30 frames, **it's working** (not frozen).

## Optimization Options

### 1. Reduce Frame Count
Generate shorter videos:
```bash
# Instead of 161 frames (10.1s)
python scripts/generate_wan22_video.py image.jpg --frames 161

# Use 81 frames (5.1s) - 2x faster interpolation
python scripts/generate_wan22_video.py image.jpg --frames 81
```

### 2. Skip Interpolation for Long Videos
Only interpolate short videos:
```bash
# Auto-detect: interpolate if <50 frames, skip if >50
if frames < 50:
    --interpolate film
else:
    --interpolate none
```

### 3. Batch Process Overnight
Queue multiple videos and let them run:
```bash
for file in input/batch/*.jpg; do
    python scripts/generate_wan22_video.py "$file" --frames 25 --interpolate film
done
```

### 4. Use Lower Resolution
Smaller videos interpolate faster:
```bash
# 512x768 is ~2x faster than 832x1216
python scripts/generate_wan22_video.py image.jpg --width 512 --height 768
```

## When To Use FILM

### Good Use Cases ✅
- Short videos (25-50 frames)
- High-quality archival content
- Slow-motion effects
- Batch processing overnight

### Poor Use Cases ❌
- Real-time/interactive workflows
- Long videos (>100 frames) when time is limited
- Low-quality source material (won't improve much)
- Content that will be compressed heavily anyway

## Alternative: Skip Interpolation

For long videos, consider generating at target FPS directly:
```bash
# Generate 161 frames @ 32fps = same 5s duration, no interpolation needed
python scripts/generate_wan22_video.py image.jpg --frames 161 --interpolate none

# Then use video editor (Premiere, DaVinci) for any frame rate conversion
# (They use optimized optical flow algorithms that are 10x faster)
```

## Technical Details

### Cache Clearing
- Small videos (<100 frames): Clear cache every 10 frames
- Large videos (>100 frames): Clear cache every 30 frames
- Tradeoff: More frequent clearing = slower but more stable

### Memory Usage
- 161 frames @ 832x1216:
  - Input tensors: ~482 MB RAM
  - GPU VRAM: ~1.5 GB
  - Temporary PNGs: ~483 MB disk (compress_level=1)
  - Interpolated PNGs: ~240 MB disk

### Why Not Batch Process?
FILM's architecture requires sequential processing for temporal coherence. Batching multiple frame pairs in parallel would:
- ❌ Break temporal smoothness
- ❌ Use 10-20GB VRAM (out of memory on most GPUs)
- ❌ Cause quality degradation

## Conclusion

**FILM is slow but high-quality**. For 161 frames:
- Expect **3-5 minutes** processing time
- Watch for "Clearing cache" messages to confirm progress
- Consider using shorter videos or skipping interpolation for long content

