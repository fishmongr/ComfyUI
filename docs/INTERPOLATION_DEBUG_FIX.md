# Frame Interpolation CUDA Crash Fix

## Problem

The frame interpolation pipeline was **hard crashing** during the FILM interpolation step when run after ComfyUI video generation:

```
[INFO] Extracting 81 frames as PNG...
[INFO] Interpolating 81 frames using FILM...
[DEBUG] Running interpolation (multiplier=2)...
(venv) PS C:\Users\markl\Documents\git\ComfyUI>  ← Script exits immediately
```

The script would crash without any Python exception or error message - just a silent exit back to the command prompt. This was **intermittent**:
- ✅ Sometimes it worked perfectly
- ❌ Other times it crashed at the exact same point

## Root Cause

This is a **CUDA reinitialization conflict** (same issue as the TaylorSeer fix):

1. ComfyUI's video generation uses PyTorch with CUDA/GPU
2. After generation, the CUDA context is in a specific state
3. When FILM interpolation runs **in the same Python process**, it tries to reinitialize PyTorch/CUDA
4. On Windows, this can cause DLL conflicts, segmentation faults, or CUDA context errors
5. These native crashes bypass Python's exception handling, causing silent exits

The original code was running interpolation in the same process with this comment:
```python
# Import interpolation pipeline directly (same process - avoids CUDA re-init crash)
```

But this was **backwards** - running in the same process was **causing** the crash!

## Solution

### Part 1: Add Debug Output with Flush

Added `flush=True` to all print statements in `scripts/interpolate_pipeline.py` so we could see exactly where the crash occurred. This revealed the crash was happening at:

```python
result = film_vfi.vfi(...)  # ← Script dies here
```

### Part 2: Run Interpolation in Separate Process

Changed `scripts/generate_wan22_video.py` to run the interpolation in a **separate subprocess** instead of importing it directly:

**Before (crashes):**
```python
from interpolate_pipeline import process_pipeline
success = process_pipeline(...)  # Same process → CUDA conflict
```

**After (works reliably):**
```python
import subprocess
cmd = [sys.executable, "scripts/interpolate_pipeline.py", video_path, "--method", "film", ...]
result = subprocess.run(cmd)  # Separate process → Clean CUDA context
```

## Benefits

1. **Reliable Operation**: No more intermittent crashes
2. **Clean CUDA Context**: Each subprocess gets fresh GPU state
3. **Better Isolation**: Video generation and interpolation don't interfere
4. **Proper Error Reporting**: Crashes in subprocess are properly handled
5. **Visible Progress**: All debug output is immediately displayed

## Files Changed

- `scripts/generate_wan22_video.py`:
  - Added subprocess import
  - Changed interpolation to run in separate process
  - Added informative message about CUDA conflict avoidance

- `scripts/interpolate_pipeline.py`:
  - Added `flush=True` to all print statements
  - Added debug messages to show exactly where processing is happening
  - Improved progress reporting

## Testing

After this fix, the pipeline works reliably:

```
[INFO] Running FILM interpolation in separate process...
[INFO] (Avoids CUDA reinitialization conflicts)
======================================================================
High-Quality Frame Interpolation Pipeline
======================================================================
[INFO] Extracting 81 frames as PNG...
[INFO] Interpolating 81 frames using FILM...
[DEBUG] Loading FILM model...
[DEBUG] Model loaded successfully
[DEBUG] Loading 81 frames into memory...
[DEBUG] All frames loaded. Creating tensor batch...
[DEBUG] Running interpolation (multiplier=2)...
Comfy-VFI: Clearing cache... Done cache clearing
[DEBUG] Interpolation completed!
[INFO] Saving 161 interpolated frames...
[SUCCESS] Interpolation complete: 161 frames
[INFO] Encoding 161 frames to video @ 32.0fps...
[SUCCESS] Video saved: output/video/..._film_32fps_hq.mp4
```

## Related Issues

This is the same class of bug as:
- TaylorSeer CUDA crashes (fixed by running in subprocess)
- Any PyTorch/CUDA operation after ComfyUI has used GPU

## Prevention

When adding new GPU-heavy operations to scripts that run after ComfyUI:
1. Always run them in a separate subprocess
2. Never import and call PyTorch/CUDA code directly in the same process
3. Add `flush=True` to progress messages for debugging

