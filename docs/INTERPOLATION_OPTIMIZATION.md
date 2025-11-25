# Frame Interpolation Optimization

## Issues Fixed

### 1. Excessive PNG File Size (3MB per frame)

**Problem**: PNGs were saved with `compress_level=0` (no compression)
- 832×1216×3 bytes = **3,035,136 bytes = 3MB per frame**
- 161 frames = **483MB of disk space!**

**Fix**: Changed to `compress_level=4`
- **Expected result**: 0.5-1MB per frame (~70% reduction)
- Still lossless PNG compression
- Slightly slower to save, but much faster overall due to less I/O

```python
# Before: NO compression
img.save(output_file, compress_level=0)  # 3MB per frame

# After: Balanced compression
img.save(output_file, compress_level=4)  # ~0.5-1MB per frame
```

### 2. Memory Lockup with Large Frame Counts

**Problem**: FILM tried to process 161 frames with cache clearing every 10 frames
- Each batch loads frames into VRAM
- 161 input frames → 321 interpolated frames
- ~1GB VRAM per 10-frame batch = **32+ batches = 32GB needed!**

**Fix**: Dynamic cache clearing based on frame count
```python
# Before: Fixed cache clearing
clear_cache_after_n_frames=10  # Always

# After: Adaptive cache clearing
if len(frames) < 100:
    clear_cache_after_n_frames = 10
else:
    # For 161 frames: 30 // 16 = ~2 frames
    clear_cache_after_n_frames = max(3, 30 // (len(frames) // 10))
```

**New behavior**:
- **<100 frames**: Clear every 10 frames (default)
- **161 frames**: Clear every **3 frames** (more frequent)
- **200+ frames**: Clear every 3 frames (minimum)

---

## Performance Impact

### Disk Space (161 frame example):

| Stage | Before | After | Savings |
|-------|--------|-------|---------|
| Input frames (161) | 483 MB | 80-160 MB | **70%** |
| Interpolated (321) | 963 MB | 160-320 MB | **70%** |
| **Total temp** | **1,446 MB** | **240-480 MB** | **70-75%** |

### Memory Usage (VRAM):

| Frames | Before | After | Improvement |
|--------|--------|-------|-------------|
| 25 frames | 3 batches | 3 batches | Same |
| 81 frames | 9 batches | 9 batches | Same |
| 161 frames | 17 batches | **54 batches** | ✅ **More frequent clearing** |

---

## Why This Matters

### PNG Compression = Lossless
- `compress_level=0`: No compression (store raw data)
- `compress_level=4`: Good compression (faster than default 6)
- `compress_level=6`: Default compression (balanced)
- `compress_level=9`: Maximum compression (slow)

**Important**: All levels are 100% lossless! Higher compression = smaller files, same quality.

### Cache Clearing
FILM loads frames into GPU VRAM in batches. Clearing cache:
- ✅ Prevents GPU OOM (out of memory)
- ✅ Allows processing larger videos
- ❌ Slightly slower (reloads frames between batches)

For 161 frames, we **need** frequent cache clearing to avoid lockups.

---

## Testing

### Quick Test (25 frames):
```bash
python scripts/generate_wan22_video.py input/test.jpg --frames 25 --interpolate film
```
**Expected**: ~30 seconds total, 50MB interpolated frames

### Medium Test (81 frames):
```bash
python scripts/generate_wan22_video.py input/test.jpg --frames 81 --interpolate film
```
**Expected**: ~2 minutes total, 160MB interpolated frames

### Large Test (161 frames):
```bash
python scripts/generate_wan22_video.py input/test.jpg --frames 161 --interpolate film
```
**Before**: Locked up, 1.4GB temp files
**After**: Should complete in ~5-7 minutes, 480MB temp files

---

## Recommendations

### For Frame Count Selection:
- **25 frames** (1.6s @ 16fps): Fast, good for testing
- **49 frames** (3.1s @ 16fps): Standard short video
- **81 frames** (5.1s @ 16fps): Longer content
- **161 frames** (10.1s @ 16fps): Maximum stable (now optimized)

### If Still Running Out of Memory:
1. Reduce `cache_clear_freq` even further (change line 137 to `max(2, ...)`)
2. Process in batches (split video into segments)
3. Upgrade GPU VRAM (8GB minimum, 12GB+ recommended)

### Disk Space Requirements:
| Frames | Resolution | Temp Space | Final Video |
|--------|-----------|------------|-------------|
| 25 | 832×1216 | ~50 MB | 0.5-1 MB |
| 81 | 832×1216 | ~160 MB | 1.5-3 MB |
| 161 | 832×1216 | ~320 MB | 3-6 MB |

Always ensure you have **3x the final video size** free for temp files.

