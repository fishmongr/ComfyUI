# Video Generation Timing Benchmarks

This document explains the timing system integrated into the video generation pipeline.

## Timing Breakdown

The script tracks and reports timing for each major stage:

### 1. **Template Load** (~0.0s)
- Loading and parsing the ComfyUI API template
- Updating template with image path and parameters
- Negligible overhead

### 2. **Queue Submit** (~2.0s)
- Submitting the prompt to ComfyUI API
- Waiting for queue confirmation
- Network latency dependent

### 3. **Video Generation** (varies by frame count)
- ComfyUI processing time
- Model inference (Wan 2.2 i2v)
- Proportional to frame count
- Examples:
  - 9 frames: ~16s
  - 25 frames: ~36s

### 4. **FILM Interpolation** (optional, varies by frame count)
- Frame extraction to PNG
- FILM model inference (2x frame count)
- H.264 encoding at specified CRF
- Examples:
  - 9→17 frames: ~6s
  - 25→49 frames: ~11s

## Example Outputs

### Short Video (9 frames) with FILM
```
TIMING SUMMARY
======================================================================
Template Load:      0.0s
Queue Submit:       2.0s
Video Generation:   16.2s
FILM Interpolation: 6.0s
----------------------------------------------------------------------
Total Time:         26.3s
```

### Full Video (25 frames) with FILM
```
TIMING SUMMARY
======================================================================
Template Load:      0.0s
Queue Submit:       2.0s
Video Generation:   36.3s
FILM Interpolation: 10.9s
----------------------------------------------------------------------
Total Time:         51.3s
```

### Video without Interpolation (9 frames)
```
TIMING SUMMARY
======================================================================
Template Load:      0.0s
Queue Submit:       2.0s
Video Generation:   16.2s
----------------------------------------------------------------------
Total Time:         20.2s
```

## Performance Notes

1. **Generation scales linearly** with frame count (~1.45s per frame)
2. **FILM interpolation scales sublinearly** (~0.44s per output frame)
3. **Total pipeline** for 25-frame video with FILM: ~51 seconds
4. **Hardware dependent**: Timings above are from a system with RTX GPU

## Time Format

- Under 60s: `X.Xs`
- Under 1 hour: `Xm Y.Ys`
- Over 1 hour: `Xh Ym Z.Zs`

## Integration

The timing system is automatically enabled and requires no configuration. It tracks:
- Individual stage durations during execution
- "Generation time" printed immediately after video completion
- "Interpolation time" printed after FILM completion
- Complete summary at the end of script execution


