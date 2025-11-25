# Avoiding Double Compression in Video Interpolation

## 🎯 The Problem

Your current workflow has **double compression**:

```
ComfyUI → 16fps H.264 MP4 → Load → Interpolate → 32fps H.264 MP4
          [Compression #1]                        [Compression #2]
          ❌ Quality loss                         ❌ More quality loss
```

Each compression pass introduces:
- **Generation loss** (irreversible quality degradation)
- **Compression artifacts** (blockiness, banding)
- **Reduced detail** (especially in interpolated frames)

## ✅ **Solution: Single Compression Pass**

### **Recommended Pipeline**

```
ComfyUI → PNG Sequence → Interpolate → Single H.264 encode → Final MP4
          [No compression]              [✅ Single compression]
```

## 📋 **Implementation Options**

### **Option 1: Use New High-Quality Pipeline Script** ⭐ RECOMMENDED

I've created `scripts/interpolate_pipeline.py` that handles everything:

```bash
# Excellent quality (CRF 18, recommended)
python scripts/interpolate_pipeline.py output/video/my-video.mp4 --method film --crf 18

# Near-lossless (CRF 10, archival quality)
python scripts/interpolate_pipeline.py output/video/my-video.mp4 --method film --crf 10

# Maximum quality (CRF 0, lossless, huge files)
python scripts/interpolate_pipeline.py output/video/my-video.mp4 --method film --crf 0
```

**What it does:**
1. Extracts video to PNG frames (lossless)
2. Interpolates frames (no compression)
3. Encodes once to final video

**File size with CRF 18:**
- Input: 458 KB (25 frames @ 16fps)
- Output: ~900-1000 KB (49 frames @ 32fps)
- Ratio: **~2.0-2.2x** ✅

---

### **Option 2: Modify ComfyUI Workflow to Save PNG Sequence**

Best for **maximum quality** and avoids any intermediate compression.

#### **Modify Your Workflow**

In `video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json`:

**Find the SaveVideo node** (probably node 108):
```json
{
  "108": {
    "inputs": {
      "video": ["107", 0],
      "filename_prefix": "video/...",
      "format": "mp4",
      "codec": "h264"
    },
    "class_type": "SaveVideo"
  }
}
```

**Option A: Save as Image Sequence**
Replace SaveVideo with a save images node to output PNG sequence:

```json
{
  "108": {
    "inputs": {
      "images": ["107", 0],  // Convert video to images
      "filename_prefix": "frames/my-sequence"
    },
    "class_type": "SaveImage"
  }
}
```

**Option B: Use both** (Save both PNG sequence + preview MP4):
```json
{
  "108": {
    // SaveImage node for PNG sequence (high quality)
  },
  "109": {
    // SaveVideo node for quick preview
  }
}
```

Then process PNGs:
```bash
python scripts/interpolate_pipeline.py --frames output/frames/my-sequence/ --fps 16 --method film
```

---

### **Option 3: Lossless Intermediate Codec**

If you want to keep video format but avoid compression artifacts:

#### **Modify SaveVideo to use FFV1 (Lossless)**

```python
# In comfy_extras/nodes_video.py, modify SaveVideo
# Or use ffmpeg to convert after:

ffmpeg -i output/video/my-video.mp4 -c:v ffv1 -level 3 output/my-video_lossless.mkv
```

Then interpolate the lossless file.

**File sizes:**
- Original H.264: 458 KB
- FFV1 lossless: ~5-10 MB (10-20x larger)
- After interpolation: ~10-20 MB
- Final re-encode: ~900 KB

---

## 📊 **Quality Comparison**

| Method | Compression Passes | Expected Quality | File Size Ratio |
|--------|-------------------|------------------|-----------------|
| **Current** | 2x (double) | ⭐⭐⭐ Good | 2-4x |
| **PNG Pipeline** | 1x (single) | ⭐⭐⭐⭐⭐ Excellent | 2-2.2x |
| **Lossless Intermediate** | 1x (single) | ⭐⭐⭐⭐⭐ Excellent | 2-2.2x |
| **Save Frames Directly** | 1x (single) | ⭐⭐⭐⭐⭐ Perfect | 2-2.2x |

---

## 🎬 **CRF Quality Guide**

CRF (Constant Rate Factor) controls quality in H.264:

```
CRF 0:   Lossless (mathematically perfect, huge files)
CRF 10:  Near-lossless (visually identical, 2-3x smaller)
CRF 15:  Transparent (cannot see compression)
CRF 18:  Excellent (recommended for archival) ⭐
CRF 20:  Very high quality (great for distribution)
CRF 23:  High quality (H.264 default)
CRF 28:  Good quality (streaming)
```

**Recommendation for your workflow:**
- **Production**: CRF 18 (excellent quality, reasonable size)
- **Archival**: CRF 10 (near-lossless)
- **Testing**: CRF 23 (fast encoding)

---

## 🚀 **Recommended Workflow**

### **Quick Start (Best Balance)**

```bash
# Process existing video with high quality (CRF 18)
python scripts/interpolate_pipeline.py output/video/polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_.mp4 --method film --crf 18
```

This will:
- ✅ Extract to PNG (no quality loss)
- ✅ Interpolate frames (no compression)
- ✅ Encode once with CRF 18 (excellent quality)
- ✅ File size: ~2x (expected)
- ✅ Quality: Maximum for final filesize

### **Maximum Quality (Near-Lossless)**

```bash
# For your best videos, use CRF 10
python scripts/interpolate_pipeline.py output/video/my-best-video.mp4 --method film --crf 10 --preset slow
```

### **For Testing/Debugging**

```bash
# Keep frames to inspect quality
python scripts/interpolate_pipeline.py output/video/test.mp4 --method film --crf 18 --keep-frames
```

---

## 💾 **Disk Space Considerations**

| Storage Method | 25 frames | 49 frames (interpolated) |
|----------------|-----------|--------------------------|
| PNG (lossless) | 50-75 MB | 100-150 MB |
| H.264 CRF 0 | ~10 MB | ~20 MB |
| H.264 CRF 10 | ~2 MB | ~4 MB |
| H.264 CRF 18 | ~500 KB | ~1 MB ✅ |
| H.264 CRF 23 | ~450 KB | ~900 KB |

**PNGs are temporary** (auto-deleted after processing unless --keep-frames).

---

## 🎯 **What Should You Do?**

### **Immediate Solution (No Workflow Changes)**

Use the new high-quality pipeline script:

```bash
# Delete old interpolated videos
del "output\video\*_film_32fps.mp4"
del "output\video\*_rife_32fps.mp4"

# Re-process with single compression pass (CRF 18)
python scripts/interpolate_pipeline.py "output/video/polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_.mp4" --method film --crf 18
```

### **Future Workflow Enhancement**

Modify ComfyUI workflow to output PNG sequence:
1. Saves maximum quality
2. No double compression ever
3. Can re-encode at any quality later

---

## 📝 **Updated Naming Convention**

```
Input:  polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_.mp4
HQ Out: polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_film_32fps_hq.mp4
```

The `_hq` suffix indicates high-quality single-compression pipeline.

---

**Bottom Line:** Use `interpolate_pipeline.py` with CRF 18 for best quality/size ratio without double compression!




