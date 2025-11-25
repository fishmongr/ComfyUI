# Frame Interpolation for ComfyUI Videos

This directory contains scripts for frame interpolation (16fps → 32fps) using RIFE or FILM.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install frame interpolation requirements
pip install -r requirements_interpolation.txt

# Optional: Install cupy for better performance (CUDA required)
# For CUDA 11.x:
pip install cupy-cuda11x

# For CUDA 12.x:
pip install cupy-cuda12x
```

### 2. Process Existing Videos

```bash
# Process a single video with RIFE (fast, recommended)
python scripts/interpolate_video.py output/video/polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_.mp4

# Process with FILM (slower, sometimes smoother)
python scripts/interpolate_video.py output/video/polar-bear_*.mp4 --method film

# Process with both methods for comparison
python scripts/interpolate_video.py output/video/polar-bear_*.mp4 --method both

# Batch process all videos in a directory
python scripts/interpolate_video.py output/video/*.mp4 --method rife
```

### 3. Generate Video with Auto-Interpolation

```bash
# Generate video and automatically interpolate with RIFE
python scripts/generate_wan22_video.py input/my-image.jpg --interpolate rife

# Generate and interpolate with FILM
python scripts/generate_wan22_video.py input/my-image.jpg --interpolate film

# Generate and create both RIFE and FILM versions
python scripts/generate_wan22_video.py input/my-image.jpg --interpolate both
```

### 4. Watch Directory for Auto-Processing

```bash
# Automatically interpolate new videos as they're created
python scripts/auto_interpolate_workflow.py --watch output/video/ --method rife

# Watch and process with both methods
python scripts/auto_interpolate_workflow.py --watch output/video/ --method both
```

### 5. Benchmark Methods

```bash
# Compare RIFE vs FILM on existing videos
python scripts/benchmark_interpolation.py output/video/

# Benchmark specific videos
python scripts/benchmark_interpolation.py output/video/polar-bear_*.mp4

# Save detailed report
python scripts/benchmark_interpolation.py output/video/ --report benchmarks/my_comparison.txt
```

## 📁 Script Descriptions

### `interpolate_video.py`
Main script for manual frame interpolation. Processes 16fps videos to 32fps.

**Features:**
- ✅ RIFE and FILM support
- ✅ Batch processing with wildcards
- ✅ Auto-downloads models on first use
- ✅ Progress bars
- ✅ Follows naming convention (`_rife_32fps`, `_film_32fps`)

### `auto_interpolate_workflow.py`
Auto-processing integration for workflow completion.

**Features:**
- ✅ Watch directory for new videos
- ✅ Auto-process on file creation
- ✅ Configurable wait time
- ✅ Both RIFE and FILM support

### `benchmark_interpolation.py`
Compare RIFE and FILM performance on your videos.

**Features:**
- ✅ Process videos with both methods
- ✅ Measure processing time
- ✅ Compare file sizes
- ✅ Generate detailed reports (TXT + JSON)

## 🎯 Output Naming Convention

The scripts follow your project's naming convention from `docs/FILENAME_GUIDE.md`:

```
Input:  polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_.mp4
RIFE:   polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_rife_32fps.mp4
FILM:   polar-bear_832x1216_25f_1.6s_4step_nosage_20251123_125650_00001_film_32fps.mp4
```

## 🔬 Method Comparison

### RIFE (Real-Time Intermediate Flow Estimation)
- **Speed**: ⚡ Fast (typically 2-5x faster than FILM)
- **Quality**: High quality, especially for fast motion
- **Best for**: General purpose, fast processing
- **Models**: Uses RIFE 4.9 (latest)

### FILM (Frame Interpolation for Large Motion)
- **Speed**: 🐢 Slower but still reasonable
- **Quality**: Very smooth, excellent for large motions
- **Best for**: High-quality output where time is not critical
- **Models**: Uses Google's FILM model

### Recommendation
Start with **RIFE** for speed and good quality. Use **FILM** if you need the smoothest possible output and have extra processing time.

## 🛠️ Advanced Usage

### Custom Output Directory
```bash
python scripts/interpolate_video.py input.mp4 --output output/interpolated/
```

### Video Info Without Processing
```bash
python scripts/interpolate_video.py output/video/*.mp4 --info
```

### Watch with Custom Wait Time
```bash
# Wait 10 seconds after file creation before processing
python scripts/auto_interpolate_workflow.py --watch output/video/ --method rife --wait 10
```

### Benchmark Limited Set
```bash
# Only benchmark first 5 videos (for quick testing)
python scripts/benchmark_interpolation.py output/video/ --limit 5
```

## 📊 Expected Performance

### Processing Speed (RTX 4090, typical)
- **RIFE**: ~100-200 fps processing speed (real-time or faster)
- **FILM**: ~30-80 fps processing speed

### File Size
- Output files are typically 1.8-2.2x the size of input files
- Quality is maintained at same bitrate

### Quality
- Both methods produce high-quality interpolation
- Minimal artifacts on most content
- 16fps → 32fps results in noticeably smoother motion

## 🐛 Troubleshooting

### "Model not found" error
Models are auto-downloaded on first use. If download fails:
1. Check your internet connection
2. Manually download models (see script comments)
3. Or use the fallback implementation (lower quality but works)

### Out of memory error
Reduce batch size or process videos one at a time:
```bash
# Process individual files instead of batch
python scripts/interpolate_video.py output/video/file1.mp4
```

### Slow processing
1. Install cupy for GPU acceleration: `pip install cupy-cuda12x`
2. Ensure CUDA is working: `python -c "import torch; print(torch.cuda.is_available())"`
3. Use RIFE instead of FILM (faster)

## 📝 Model Storage

Models are automatically downloaded to:
```
models/frame_interpolation/
├── rife49.pkl              # RIFE 4.9 model
└── film_net_fp32.pt        # FILM model
```

## 🔗 References

- RIFE: https://github.com/hzwer/Practical-RIFE
- FILM: https://github.com/google-research/frame-interpolation
- ComfyUI Frame Interpolation Node: Already installed in `custom_nodes/ComfyUI-Frame-Interpolation/`

---

**Last Updated**: 2025-11-24
**Scripts**: `interpolate_video.py`, `auto_interpolate_workflow.py`, `benchmark_interpolation.py`




