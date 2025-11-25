# PNG + FILM Workflow - Complete Solution

## ✅ What's Been Created

### **1. New Workflow**
**File:** `user/default/workflows/video_wan2_2_14B_i2v_PNG_FILM.json`

- Outputs PNG frame sequence instead of MP4 video
- No compression before interpolation
- Production-quality pipeline (matches Fal.ai approach)

### **2. New Generation Script**  
**File:** `scripts/generate_wan22_video_film.py`

Handles the complete pipeline:
1. Generates video as PNG frames (no compression)
2. Automatically runs FILM interpolation (16fps → 32fps)
3. Encodes final video with CRF 18 (excellent quality)
4. Single compression pass (no double compression)

---

## 🚀 Usage

### **Basic Usage** (Recommended)

```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Generate 25-frame video with automatic FILM interpolation
python scripts/generate_wan22_video_film.py input/my-image.jpg
```

**This will:**
- Generate 25 frames @ 16fps as PNG (no compression)
- Interpolate to 49 frames @ 32fps with FILM
- Encode once to final MP4 with CRF 18 (excellent quality)
- Output: `output/video/my-image_..._film_32fps_hq.mp4`

### **Custom Frame Count**

```bash
# 5-second video (81 frames)
python scripts/generate_wan22_video_film.py input/my-image.jpg --frames 81

# 10-second video (161 frames)
python scripts/generate_wan22_video_film.py input/my-image.jpg --frames 161
```

### **Quality Control**

```bash
# Maximum quality (CRF 10, near-lossless, larger files)
python scripts/generate_wan22_video_film.py input/my-image.jpg --crf 10

# Standard quality (CRF 23, smaller files)
python scripts/generate_wan22_video_film.py input/my-image.jpg --crf 23

# Excellent quality (CRF 18, default, best balance)
python scripts/generate_wan22_video_film.py input/my-image.jpg --crf 18
```

###  **Skip Interpolation** (PNG frames only)

```bash
# Generate PNG frames only, no interpolation
python scripts/generate_wan22_video_film.py input/my-image.jpg --no-film

# Then interpolate manually later
python scripts/interpolate_pipeline.py --frames output/frames/my-image_*/ --fps 16 --method film --crf 18
```

---

## 📊 Workflow Comparison

| Aspect | Old Workflow (MP4) | New Workflow (PNG + FILM) |
|--------|-------------------|---------------------------|
| **Generation output** | MP4 video | PNG frames |
| **Save time** | 3-5s | 0.5-1s (faster!) |
| **Intermediate compression** | Yes (H.264) | No (lossless PNG) |
| **Interpolation quality** | Re-compressed | Perfect (no prior compression) |
| **Final compression passes** | 2x (double) | 1x (single) |
| **File size** | 3.8x (bloated) | 2.0x (expected) |
| **Workflow type** | Amateur | **Production** ⭐ |

---

## 🎯 Expected Results

### **For 25-frame video (832x1216):**

**Old workflow:**
- Generation: MP4 (458 KB, compressed)
- FILM interpolation: 1,733 KB (3.8x, bloated from double compression)
- Quality: Good (but double compressed)

**New workflow:**
- Generation: PNG frames (~75 MB temp, deleted after)
- FILM interpolation: ~900 KB (2.0x, single compression)
- Quality: Excellent (no double compression)

---

## ⚙️ How It Works

### **Pipeline Flow:**

```
1. ComfyUI Workflow
   Input image → Two-pass generation → PNG frames
   Output: output/frames/my-image_832x1216_25f.../

2. Automatic FILM Interpolation
   PNG frames (25 @ 16fps) → FILM → PNG frames (49 @ 32fps)
   Still no compression

3. Single Encode Pass
   Interpolated PNGs → FFmpeg H.264 CRF 18 → Final MP4
   Output: output/video/my-image_..._film_32fps_hq.mp4
```

**Key advantage:** Video codec is only applied once, at the very end.

---

## 📁 Output Files

### **Naming Convention:**

```
PNG frames:
  output/frames/polar-bear_832x1216_25f_1.6s_4step_nosage_20251124_103045/

Final video:
  output/video/polar-bear_832x1216_25f_1.6s_4step_nosage_20251124_103045_film_32fps_hq.mp4
```

The `_hq` suffix indicates high-quality single-compression pipeline.

---

## 🔧 Prerequisites

### **1. FFmpeg** (Required for interpolation)

```bash
# Install ffmpeg
choco install ffmpeg

# Verify
ffmpeg -version
```

### **2. Python Dependencies** (Already installed)

```bash
pip install opencv-python torch numpy tqdm
```

---

## 📝 Full Example

```bash
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Generate video with FILM interpolation
python scripts/generate_wan22_video_film.py input/sogni-photobooth-my-polar-bear-baby-raw.jpg --frames 49 --crf 18

# Expected output:
# [INFO] Generating 49 frames @ 16fps as PNG...
# [SUCCESS] PNG frames saved: output/frames/my-polar-bear-baby_832x1216_49f_3.1s_4step_nosage_20251124_103045/
# [INFO] FILM interpolation: 49 frames → 97 frames...
# [SUCCESS] Final video: output/video/my-polar-bear-baby_832x1216_49f_3.1s_4step_nosage_20251124_103045_film_32fps_hq.mp4
# [INFO] File size: ~1.8 MB (2.0x, expected)
#
# Delete PNG frames? (y/N): y
# [INFO] Deleted frames: output/frames/...
```

---

## 🎨 Quality Settings Guide

| CRF | Quality | File Size | Use Case |
|-----|---------|-----------|----------|
| 0-10 | Near-lossless | 2-3x | Archival, maximum quality |
| 15-18 | Excellent | 1.3-1.5x | **Production (recommended)** ⭐ |
| 19-23 | High | 1.0-1.2x | Distribution, sharing |
| 24-28 | Good | 0.8-1.0x | Streaming, social media |

**Recommendation:** Use CRF 18 for best quality/size balance.

---

## 🆚 vs. Fal.ai Approach

**What Fal.ai does:**
- Generates frames in memory or as temp PNG
- Interpolates (if requested)
- Encodes once to final video
- Single compression pass

**What you now do:**
- ✅ Generate frames as PNG (same)
- ✅ Interpolate with FILM (same)
- ✅ Encode once to final video (same)
- ✅ Single compression pass (same)

**You now have a production-grade pipeline!** 🎉

---

## 🐛 Troubleshooting

### **"FFmpeg not found"**
```bash
choco install ffmpeg
# Or download from https://ffmpeg.org/download.html
```

### **"Workflow template not found"**
```bash
python scripts/create_png_workflow.py
```

### **Frames directory not found**
Check `output/frames/` directory manually. The script will show the expected path.

### **Out of disk space**
PNG frames use ~75 MB for 25 frames. Clean up old frame directories in `output/frames/`.

---

## ✅ Advantages Over Old Method

1. **Faster generation** (PNG save is 3-5x faster than video encoding)
2. **Better quality** (no double compression)
3. **Correct file size** (2x instead of 3.8x)
4. **Production workflow** (matches Fal.ai, Replicate, etc.)
5. **Flexible** (can re-encode at different quality later)
6. **Debuggable** (can inspect PNG frames if needed)

---

## 📚 Related Documentation

- `docs/PRODUCTION_PRACTICES.md` - How Fal.ai does it
- `docs/PNG_VS_VIDEO_PERFORMANCE.md` - Performance analysis
- `docs/COMPRESSION_QUALITY.md` - Quality deep dive
- `docs/INTERPOLATION_UPDATE.md` - Issues fixed

---

**Status:** ✅ Ready to use  
**Quality:** Production-grade  
**Recommended for:** All new videos  

**Start using now:**
```bash
python scripts/generate_wan22_video_film.py input/your-image.jpg
```

🎬 **Enjoy your high-quality, properly compressed videos!**




