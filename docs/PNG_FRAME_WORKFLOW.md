# PNG Frame Workflow Explanation

## Your Questions Answered

### 1. Do platforms like Fal.ai save PNGs instead of video?

**Most likely YES.** Here's why:

Production platforms like Fal.ai typically:
1. ✅ **Save PNG/EXR frames directly from the diffusion model** (no video encoding)
2. ✅ **Run interpolation on those frames** (FILM/RIFE)
3. ✅ **Encode once to final video** (single H.264 compression)

This gives them:
- **True single compression** (no quality loss from decode/re-encode)
- **Perfect 2.0x file size** for 2x interpolation
- **Maximum flexibility** (can generate different qualities/formats from same frames)

### 2. Can ComfyUI save video without compression?

**NO - ComfyUI's SaveVideo node does NOT expose quality controls.**

Looking at the code:

```python
# comfy_api/latest/_input_impl/video_types.py, line 275
video_stream = output.add_stream('h264', rate=frame_rate)
video_stream.width = self.__components.images.shape[2]
video_stream.height = self.__components.images.shape[1]
video_stream.pix_fmt = 'yuv420p'
# NO CRF, NO BITRATE, NO QUALITY OPTIONS!
```

**ComfyUI uses default H.264 encoding with no quality parameters exposed.**

This means:
- ❌ No CRF control (uses encoder defaults)
- ❌ No bitrate control
- ❌ No preset selection
- ❌ No lossless option
- ✅ Only format (MP4) and codec (H.264) can be changed

**Interesting exception**: The `SaveWEBM` node DOES have CRF control:
```python
# comfy_extras/nodes_video.py, line 29
io.Float.Input("crf", default=32.0, min=0, max=63.0, step=1)
```

But your workflow uses `SaveVideo` for MP4, which doesn't have this.

---

## What This Means For Your Workflow

### Current Reality:
```
ComfyUI generates → video.mp4 (H.264, default quality, COMPRESSED ❌)
                     ↓
Extract frames    → PNGs (lossless decode, but data already lost)
                     ↓
FILM interpolate  → Interpolated PNGs
                     ↓
FFmpeg encode     → final.mp4 (H.264, CRF 18, COMPRESSED ❌)
```

**Result**: Double compression, ~1.5-1.7x file size instead of 2.0x

### What Fal.ai Likely Does:
```
Diffusion model   → PNG frames (NO compression ✓)
                     ↓
FILM interpolate  → Interpolated PNGs
                     ↓
FFmpeg encode     → final.mp4 (H.264, SINGLE compression ✓)
```

**Result**: Single compression, true 2.0x file size

---

## Solution Options

### Option 1: Use SaveImage Instead of SaveVideo (Recommended)

**Pros:**
- ✅ True single compression
- ✅ Maximum quality
- ✅ Smaller final file size
- ✅ Same workflow as Fal.ai

**Cons:**
- ❌ 25 PNG files = ~75 MB disk space during processing (vs 0.4 MB for MP4)
- ❌ Requires workflow modification
- ❌ No preview video until after interpolation

**How to implement:**
We actually started working on this earlier! You have:
- `scripts/create_png_workflow.py` - Creates PNG-output workflow
- `workflows/video_wan2_2_14B_i2v_PNG_FILM.json` - PNG workflow (needs fixing)

### Option 2: Keep Current Workflow (Acceptable)

The double compression with your current settings is minimal because:
- ComfyUI's default H.264 quality is decent
- Your CRF 18 for final encode is high quality
- File size penalty is only 1.5-1.7x instead of 2.0x
- Quality loss is imperceptible for most content

**When this matters:**
- Archival/professional work requiring maximum quality
- Detailed textures/high-frequency content
- Further editing/processing planned

**When this is fine:**
- Social media/web distribution
- Most consumer content
- Current results look good to you

### Option 3: Hack ComfyUI SaveVideo (Advanced)

You could modify `comfy_api/latest/_input_impl/video_types.py` line 275 to add CRF:

```python
video_stream = output.add_stream('h264', rate=frame_rate)
video_stream.options = {'crf': '10'}  # Near-lossless
```

But this:
- ❌ Requires modifying ComfyUI core
- ❌ Gets overwritten on ComfyUI updates
- ❌ Still doesn't eliminate double compression

---

## Recommendation

**For production-quality work matching Fal.ai:**
→ Modify workflow to save PNGs instead of video

**For current "good enough" quality:**
→ Keep existing workflow, it's working fine

The quality difference is honestly minimal at CRF 18. Your file size of 1.5-1.7x shows the compression is efficient. Unless you're doing professional/archival work, the current approach is a reasonable trade-off.

---

## How Platforms Handle This

| Platform | Approach | Why |
|----------|----------|-----|
| **Fal.ai** | PNG frames → FILM → MP4 | Maximum quality, single compression |
| **Runway** | PNG frames → Encode | Same as Fal.ai |
| **Replicate** | PNG frames → Process → MP4 | Industry standard |
| **Your workflow** | MP4 → PNG → FILM → MP4 | Convenient, uses existing templates |

Production platforms prioritize quality over disk space, so they save frames during generation.

