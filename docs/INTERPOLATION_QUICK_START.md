# Frame Interpolation Quick Reference

## 📋 Common Commands

### Process Single Video
```bash
# RIFE (fast)
python scripts/interpolate_video.py output/video/my-video.mp4

# FILM (slower, smoother)
python scripts/interpolate_video.py output/video/my-video.mp4 --method film

# Both methods for comparison
python scripts/interpolate_video.py output/video/my-video.mp4 --method both
```

### Batch Process Multiple Videos
```bash
# All polar-bear videos with RIFE
python scripts/interpolate_video.py output/video/polar-bear*.mp4 --method rife

# All videos in directory
python scripts/interpolate_video.py output/video/*.mp4 --method rife

# Process with both methods
python scripts/interpolate_video.py output/video/*.mp4 --method both
```

### Generate Video with Auto-Interpolation
```bash
# Generate 25 frames and auto-interpolate with RIFE
python scripts/generate_wan22_video.py input/my-image.jpg --interpolate rife

# Generate 81 frames (5s) and interpolate with FILM
python scripts/generate_wan22_video.py input/my-image.jpg --frames 81 --interpolate film

# Generate and create both RIFE and FILM versions
python scripts/generate_wan22_video.py input/my-image.jpg --interpolate both
```

### Auto-Watch Directory
```bash
# Watch for new videos and auto-interpolate with RIFE
python scripts/auto_interpolate_workflow.py --watch output/video/ --method rife

# Watch and process with both methods
python scripts/auto_interpolate_workflow.py --watch output/video/ --method both
```

### Benchmark Methods
```bash
# Compare RIFE vs FILM on all videos
python scripts/benchmark_interpolation.py output/video/

# Benchmark specific videos
python scripts/benchmark_interpolation.py output/video/polar-bear*.mp4 --report benchmarks/polar_bear_test.txt

# Quick test on first 3 videos
python scripts/benchmark_interpolation.py output/video/ --limit 3
```

## 🎯 Output Files

Your videos follow the naming convention:

```
Input:  polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_.mp4
RIFE:   polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_rife_32fps.mp4
FILM:   polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_film_32fps.mp4
```

## 🔍 Check Video Info
```bash
python scripts/interpolate_video.py output/video/*.mp4 --info
```

## ⚡ Performance

### RIFE (Recommended for most use cases)
- Speed: ~20 fps processing (1.3s for 25-frame video)
- Quality: High
- File size: ~5x original (2.33 MB for 0.45 MB input)
- Best for: Fast processing with good quality

### FILM (Fallback mode currently)
- Speed: ~97 fps processing (0.3s for 25-frame video)
- Quality: Good (using simple blending fallback)
- File size: ~4x original (1.69 MB for 0.45 MB input)
- Best for: Quick processing

**Note**: Full FILM model loading is not working yet, currently using fast fallback. RIFE is recommended.

## 🐛 Troubleshooting

### Scripts not found
Make sure you're in the ComfyUI root directory:
```bash
cd c:\Users\markl\Documents\git\ComfyUI
```

### Python not found
Activate the virtual environment:
```bash
.\venv\Scripts\Activate.ps1
```

### Out of memory
Process videos one at a time instead of batch.

## 📚 Full Documentation
See `docs/FRAME_INTERPOLATION.md` for complete documentation.

---
**Last Updated**: 2025-11-24




