# Wan 2.2 S2V (Sound-to-Video) Guide

## Overview

The `generate_wan22_sound_video.py` script generates videos **synchronized to audio** using the Wan 2.2 S2V model. Motion, timing, and dynamics are driven by the audio, with optional reference images for visual style.

## Quick Start

### Basic Audio-Only Generation

```bash
python scripts/generate_wan22_sound_video.py input/music.mp3
```

Generates a ~4.8s video (77 frames) with motion driven by the audio.

### With Reference Image

```bash
python scripts/generate_wan22_sound_video.py input/music.mp3 --ref-image input/album-art.jpg
```

The reference image provides visual style/subject while audio drives the motion.

### Longer Videos

```bash
# 19 second video
python scripts/generate_wan22_sound_video.py input/song.mp3 --frames 305
```

## Audio Format Support

✅ **Supported Formats** (via PyAV - universal audio loading):

| Format | Extension | Notes |
|--------|-----------|-------|
| **WAV** | `.wav` | Uncompressed, best quality |
| **MP3** | `.mp3` | Most common, widely supported |
| **M4A/AAC** | `.m4a`, `.aac` | Apple formats, good quality |
| **FLAC** | `.flac` | Lossless compression |
| **OGG Vorbis** | `.ogg` | Open source |
| **Opus** | `.opus` | Low latency |
| **WMA** | `.wma` | Windows Media Audio |

**All audio is automatically resampled to 16kHz** for the audio encoder.

## Audio Start Time & Duration

### Use Part of a Long Audio File

```bash
# Start at 30 seconds, use 5 seconds of audio, generate 81 frames (~5s video)
python scripts/generate_wan22_sound_video.py input/long-song.mp3 \
  --audio-start 30 \
  --audio-duration 5 \
  --frames 81
```

### Parameters

- `--audio-start`: Start time in seconds (default: 0.0)
- `--audio-duration`: Duration in seconds (default: auto-calculated from frames)

**How it works:**
1. Loads full audio file
2. Trims to specified segment (using `TrimAudioDuration` node)
3. Encodes only the trimmed segment
4. Generates video synchronized to that segment

**Use cases:**
- **Extract best parts**: Skip intro, use chorus
- **Avoid silence**: Start after long intro
- **Test quickly**: Use short segments for testing
- **Long songs**: Process in chunks

## Complete Usage Examples

### Example 1: Music Video with Album Art

```bash
python scripts/generate_wan22_sound_video.py \
  input/song.mp3 \
  --ref-image input/album-cover.jpg \
  --frames 161 \
  --positive "vibrant colors, dynamic movement, musical energy" \
  --negative "static, dull, boring"
```

### Example 2: Audio Visualization

```bash
# Pure audio visualization (no reference image)
python scripts/generate_wan22_sound_video.py \
  input/podcast.mp3 \
  --frames 77 \
  --positive "abstract visualization, flowing shapes, audio reactive" \
  --negative "realistic, photographic"
```

### Example 3: Dance Video

```bash
python scripts/generate_wan22_sound_video.py \
  input/dance-music.mp3 \
  --ref-image input/dancer.jpg \
  --frames 305 \
  --positive "energetic dance, rhythmic motion, synchronized movement" \
  --negative "slow, static, off-beat"
```

### Example 4: Extract Specific Segment

```bash
# Use 15 seconds starting from 1:30 (90s) into the song
python scripts/generate_wan22_sound_video.py \
  input/full-song.mp3 \
  --audio-start 90 \
  --audio-duration 15 \
  --frames 241 \
  --ref-image input/artist-photo.jpg
```

### Example 5: With FILM Interpolation

```bash
# Generate 16fps, then interpolate to 32fps (audio sync preserved!)
python scripts/generate_wan22_sound_video.py \
  input/music.mp3 \
  --frames 161 \
  --interpolate film \
  --crf 18
```

**What happens:**
1. Generates 161 frames @ 16fps (10s) synced to audio
2. FILM interpolates visual frames to 322 frames @ 32fps (still 10s)
3. Audio track passes through unchanged
4. Result: **2x smoother motion, perfect audio sync maintained!**

**Benefits for S2V:**
- Audio-driven motion looks even better at 32fps
- Smoother dance/performance movements
- Better for fast music
- Same audio sync, enhanced visuals

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `audio_path` | Path to audio file (required) | - |
| `--ref-image` | Reference image for style/subject | None |
| `--frames` | Number of frames to generate | 77 (~4.8s) |
| `--audio-start` | Start time in audio (seconds) | 0.0 |
| `--audio-duration` | Duration of audio to use (seconds) | Auto |
| `--width` | Video width | 832 |
| `--height` | Video height | 1216 |
| `--positive` | Positive prompt | Template default |
| `--negative` | Negative prompt | Template default |
| `--settings` | Settings tag for filename | s2v |
| `--interpolate` | FILM interpolation (film/none) | none |
| `--crf` | Quality for interpolated video | 18 |
| `--timeout` | Generation timeout (seconds) | Auto |
| `--url` | ComfyUI URL | http://localhost:8188 |

## Frame Count Recommendations

**Resolution: 832x1216 (9:16 portrait)**

| Frames | Duration @ 16fps | Audio Duration | Use Case |
|--------|-----------------|----------------|----------|
| 77 | 4.8s | ~5s | Quick test, short clip |
| 161 | 10.1s | ~10s | Standard music clip |
| 241 | 15.1s | ~15s | Extended scene |
| 305 | 19.1s | ~20s | Full verse/chorus |

**Formula:** `frames = duration_seconds * 16 + 1`

**Note:** Audio duration should match video duration for best sync.

## Model Requirements

✅ **You already have everything needed:**

- **S2V Model**: `wan2.2_s2v_14B_fp8_scaled.safetensors` (16GB)
- **Audio Encoder**: `wav2vec2_large_english_fp16.safetensors` (600MB)
- **VAE**: `wan_2.1_vae.safetensors` (shared with i2v)
- **Text Encoder**: `umt5_xxl_fp8_e4m3fn_scaled.safetensors` (shared)

**Total VRAM Usage:** ~25-31 GB (fits perfectly on your RTX 5090 32GB)

## S2V vs I2V Comparison

| Feature | I2V (Image-to-Video) | S2V (Sound-to-Video) |
|---------|---------------------|---------------------|
| **Primary Input** | Image(s) | Audio + optional image |
| **Motion Driver** | Prompts + frames | Audio rhythm/timing |
| **Sync** | Manual (via prompts) | Automatic (audio-driven) |
| **Best For** | Photo animation | Music videos, audio viz |
| **Frame Range** | 25-161 (1-10s) | 77-305 (5-20s) |
| **Model** | `wan2.2_i2v_*` | `wan2.2_s2v` |
| **Script** | `generate_wan22_video.py` | `generate_wan22_sound_video.py` |

## Tips for Best Results

### 1. Reference Image Selection

**With reference image:**
- Provides consistent style/subject
- Motion still driven by audio
- Best for: music videos, artist performances

**Without reference image:**
- Pure audio visualization
- More abstract/creative
- Best for: audio-reactive art, visualizations

### 2. Audio Segment Selection

```bash
# Find the best part
# - Skip long intros
# - Use chorus or bridge
# - Avoid silence/fade-outs
--audio-start 30 --audio-duration 10
```

### 3. Prompt Strategy

**For music/rhythm:**
```bash
--positive "rhythmic motion, synchronized movement, dynamic energy, pulsing to beat"
```

**For calm audio:**
```bash
--positive "smooth flowing motion, gentle movements, serene atmosphere, soft dynamics"
```

**For speech/podcast:**
```bash
--positive "subtle motion, speaking gestures, natural animation, conversational flow"
```

### 4. Frame Count Guidelines

- **Fast/energetic music**: More frames for smoother motion
- **Slow/ambient**: Fewer frames work well
- **Match audio**: Video duration should match audio segment

## Output Files

Files saved to `output/video/` with naming pattern:

```
{source}_{width}x{height}_{frames}f_{duration}_{has_ref}_{settings}_{timestamp}.mp4
```

Where `{has_ref}` is:
- `with_ref` - Reference image provided
- `no_ref` - Audio-only generation

**Example:**
```
output/video/my-song_832x1216_161f_10.1s_with_ref_s2v_20250125_143022.mp4
```

## Troubleshooting

### First Frame Has Wrong Color/Contrast
**Issue**: First frame may appear slightly "overbaked" with different brightness/contrast  
**Cause**: Known VAE limitation in the Wan 2.2 S2V model  
**Workaround**: The official workflow includes a complex "double first frame" hack, but it's not yet integrated into our script. For now, you can:
- Manually replace the first frame in post-processing
- Or just ignore it - usually barely noticeable in motion
- A proper fix requires careful integration testing

### "Audio file not found"
- Check file path is correct
- Use absolute or relative path from project root

### "Unsupported audio format"
- Script will attempt to load anyway (PyAV supports most formats)
- If it fails, convert to WAV/MP3 first

### Video not synced to audio
- Ensure `--audio-duration` matches video duration (frames/16)
- Default behavior auto-calculates duration from frames

### VRAM out of memory
- Reduce resolution (e.g., `--width 640 --height 960`)
- Use shorter videos (fewer frames)
- Your RTX 5090 32GB should handle standard sizes easily

### Generation too slow
- S2V is slower than I2V (more complex processing)
- Typical: 60-120s per pass for 77 frames
- Longer videos scale proportionally

## Advanced: Chaining Videos

For very long audio (>20s), generate in segments:

```bash
# Segment 1: 0-10s
python scripts/generate_wan22_sound_video.py input/long-song.mp3 \
  --audio-start 0 --audio-duration 10 --frames 161 --ref-image input/img.jpg

# Segment 2: 10-20s  
python scripts/generate_wan22_sound_video.py input/long-song.mp3 \
  --audio-start 10 --audio-duration 10 --frames 161 --ref-image input/img.jpg

# Then concatenate with ffmpeg
ffmpeg -i segment1.mp4 -i segment2.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1[v]" -map "[v]" output.mp4
```

## Performance Benchmarks (RTX 5090)

| Frames | Resolution | Time (est.) | VRAM |
|--------|-----------|-------------|------|
| 77 | 832x1216 | ~90-150s | ~25GB |
| 161 | 832x1216 | ~180-300s | ~28GB |
| 305 | 832x1216 | ~300-500s | ~30GB |

**Note:** Times include audio encoding + video generation. No two-pass needed (unlike i2v).

## Technical Details

**Audio Processing Pipeline:**
```
Audio File (any format)
    │
    ├──→ Load via PyAV (supports all formats)
    │
    ├──→ Optional: Trim (start time + duration)
    │
    ├──→ Resample to 16kHz (Wav2Vec2 requirement)
    │
    ├──→ Wav2Vec2 Audio Encoder
    │         │
    │         └──→ 25 layers of audio embeddings
    │                   │
    │                   └──→ Temporal audio features
    │
    └──→ WanSoundImageToVideo
              ├── audio_encoder_output (audio embeddings)
              ├── ref_image (optional style/subject)
              ├── positive/negative prompts
              └── width/height/frames
                    │
                    ▼
              Video synchronized to audio
```

**Key Differences from I2V:**
- Single-pass generation (no high/low noise split)
- Audio embeddings drive motion timing
- Longer typical durations (5-20s vs 1-10s)
- No LoRAs needed

## Next Steps

1. **Test basic generation**: Try with a short audio file
2. **Add reference image**: See how it affects style
3. **Experiment with segments**: Use `--audio-start` for best parts
4. **Try different formats**: MP3, WAV, FLAC all work
5. **Adjust prompts**: Guide the visual style

Enjoy creating audio-synchronized videos! 🎵🎬

