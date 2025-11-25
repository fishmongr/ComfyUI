# Frame Interpolation Installation Guide

## Recommended Custom Nodes for RIFE and FILM

### Option 1: ComfyUI-Frame-Interpolation (RECOMMENDED)
**Repository**: https://github.com/Fannovel16/ComfyUI-Frame-Interpolation

**Features:**
- Supports both RIFE and FILM
- Multiple RIFE versions (4.6, 4.15, 4.22)
- FILM (Google's Frame Interpolation for Large Motion)
- Optimized for ComfyUI
- Active development

**Installation via ComfyUI-Manager:**
1. Start ComfyUI
2. Open Manager (gear icon)
3. Search: "Frame Interpolation"
4. Install "ComfyUI-Frame-Interpolation by Fannovel16"
5. Restart ComfyUI

**Models to Download:**
- RIFE 4.22 (recommended for quality/speed balance)
- FILM L1 (best quality, slower)
- FILM VGG (good quality, faster)

### Option 2: ComfyUI-VideoHelperSuite
**Repository**: https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite

**Features:**
- Comprehensive video toolkit
- Frame interpolation support
- Video loading/saving
- Frame manipulation
- Audio handling

**Installation:**
Same process via ComfyUI-Manager, search "VideoHelperSuite"

## Integration with Wan 2.2 Workflow

### Workflow Structure (16fps → 32fps):

```
[Wan 2.2 Two-Pass Generation]
         ↓
   (81 frames @ 16fps = 5s video)
         ↓
[Frame Interpolation - RIFE or FILM]
         ↓
   (162 frames @ 32fps = 5s video)
         ↓
[Save Video @ 32fps]
```

### Node Setup:

**After VAE Decode (video frames):**
1. Add RIFE/FILM interpolation node
2. Set multiplier: 2x (16fps → 32fps)
3. Connect to video save node
4. Set output fps: 32

### Performance Expectations:

**RIFE 4.22:**
- Speed: ~10-20s for 81→162 frames
- Quality: Excellent for most motion
- VRAM: Low overhead (~1-2GB)

**FILM:**
- Speed: ~20-40s for 81→162 frames
- Quality: Best for complex motion
- VRAM: Moderate overhead (~2-3GB)

## Testing Strategy

### Compare Both Interpolators:

1. **RIFE Test**:
   - Run Wan 2.2 two-pass (67-80s target)
   - Interpolate with RIFE (expect ~15s)
   - Total: ~85-95s for 5s@32fps

2. **FILM Test**:
   - Same Wan 2.2 generation
   - Interpolate with FILM (expect ~25s)
   - Total: ~95-105s for 5s@32fps

3. **Quality Assessment**:
   - Side-by-side comparison
   - Check motion smoothness
   - Look for artifacts
   - Temporal consistency

### Success Criteria:

- **Target**: Total pipeline < 180s for 5s@32fps
- **RIFE**: Should easily meet target (~95s total)
- **FILM**: Should meet target with margin (~105s total)
- **Quality**: No visible artifacts, smooth motion

## Installation Steps

### Via ComfyUI-Manager (EASIEST):

```batch
# Start ComfyUI with your optimized script
cd C:\Users\markl\Documents\git\ComfyUI
.\scripts\launch_wan22_rtx5090.bat

# Then in ComfyUI web interface:
# 1. Click Manager button
# 2. Click "Install Custom Nodes"
# 3. Search "Frame Interpolation"
# 4. Install "ComfyUI-Frame-Interpolation"
# 5. Restart ComfyUI
```

### Manual Installation (if needed):

```batch
cd C:\Users\markl\Documents\git\ComfyUI\custom_nodes
git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation
cd ComfyUI-Frame-Interpolation
..\..\ venv\Scripts\activate
pip install -r requirements.txt
```

## Model Downloads

Models will auto-download on first use, or manually download:

**RIFE Models:**
- Place in: `ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/ckpts`
- RIFE 4.22: Auto-downloads from HuggingFace

**FILM Models:**
- Place in: `ComfyUI/custom_nodes/ComfyUI-Frame-Interpolation/film_models`
- FILM L1: Auto-downloads from Google Research

## Next Steps

1. Install ComfyUI-Frame-Interpolation via Manager
2. Test RIFE interpolation first (faster)
3. Test FILM interpolation
4. Compare results
5. Choose best interpolator for production
6. Document in final optimization guide

## Why 32fps Instead of 30fps?

- 32 is even doubling of 16 (cleaner math)
- No fractional frames needed
- Better for future 2x, 4x, 8x cascading
- Still smooth playback
- Can always convert to 30fps in post if needed

