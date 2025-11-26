# Wan 2.2 S2V Tips & Tricks for Better Results

## Improving Lip Sync and Audio-Driven Motion

### 1. Reference Image Selection (Most Important!)

**The reference image dramatically affects lip sync quality.**

✅ **Good reference images:**
- **Clear, well-lit face** - Good lighting on the subject
- **Neutral or slightly open mouth** - Easier for model to animate
- **Forward-facing** - Direct eye contact with camera
- **High resolution** - At least 1024px on the shortest side
- **Single subject** - One clear person in frame
- **Minimal occlusion** - No hands covering mouth, no glasses

❌ **Avoid:**
- Side profiles or turned heads
- Closed mouths or tight lips
- Heavy makeup or filters
- Multiple people
- Low resolution or blurry images
- Strong shadows on face

**Example prompts for reference image:**
```bash
# Good - Clear, frontal portrait
--ref-image portrait_woman_neutral_expression.jpg

# Better - Professional headshot style
--ref-image headshot_singer_slight_smile.jpg
```

### 2. Prompt Engineering for Lip Sync

**Be explicit about speech and singing:**

✅ **Good prompts:**
```bash
--positive "woman singing passionately into microphone, mouth moving to lyrics, expressive facial movements, professional performance"

--positive "person speaking directly to camera, natural lip movements, animated facial expressions, engaging delivery"

--positive "singer performing ballad, emotional lip sync, subtle mouth movements, intimate performance"
```

❌ **Vague prompts:**
```bash
--positive "woman with music"  # Too vague
--positive "singing"  # Not enough detail
```

**Key phrases to include:**
- "lip sync", "mouth moving", "singing", "speaking"
- "expressive facial movements"
- "animated expressions"
- "natural mouth movements"
- "performance", "engaging"

### 3. Audio Quality Matters

**Clean, clear audio produces better sync:**

✅ **Best audio:**
- **Vocals prominent** in the mix
- **Minimal background noise**
- **Clear pronunciation**
- **Moderate tempo** - Not too fast
- **Studio quality** or good recording

❌ **Problematic audio:**
- Heavy instrumental drowning out vocals
- Rap/fast speech (very challenging)
- Mumbled or unclear vocals
- Low bitrate/compressed audio
- Heavy reverb or effects

**Audio preprocessing tips:**
```bash
# Use vocal-isolated tracks when possible
# Tools: Spleeter, Ultimate Vocal Remover
python -m spleeter separate -p spleeter:2stems audio.mp3

# Use the vocals_only.wav output as input
python scripts/generate_wan22_sound_video.py vocals_only.wav --ref-image face.jpg
```

### 4. Frame Count and Duration

**Shorter clips often have better sync:**

✅ **Recommended durations:**
- **77 frames (4.8s)** - Default, good balance
- **97 frames (6s)** - Still manageable
- **161 frames (10s)** - Pushing the limit

❌ **Challenging:**
- **305+ frames (19s+)** - Sync tends to drift
- Very long continuous segments

**For longer videos:**
Process in chunks and concatenate:
```bash
# Generate 3 separate 10-second clips
python scripts/generate_wan22_sound_video.py song.mp3 --audio-start 0 --audio-duration 10 --frames 161 --settings part1
python scripts/generate_wan22_sound_video.py song.mp3 --audio-start 10 --audio-duration 10 --frames 161 --settings part2
python scripts/generate_wan22_sound_video.py song.mp3 --audio-start 20 --audio-duration 10 --frames 161 --settings part3

# Then concatenate with ffmpeg
ffmpeg -i part1.mp4 -i part2.mp4 -i part3.mp4 -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" -map "[v]" -map "[a]" full_song.mp4
```

### 5. Resolution and Aspect Ratio

**Face size in frame affects lip sync:**

✅ **Best for lip sync:**
- **Portrait mode (9:16)**: 832x1216 (default)
  - Face fills more of frame
  - Better detail on facial features
- **Square (1:1)**: 1024x1024
  - Good balance
- **Close-up shots** in reference image

❌ **Harder for lip sync:**
- **Wide landscape shots** with small face
- **Full body shots** where face is tiny
- Very wide aspect ratios

### 6. Model Settings

**Current optimal settings (already in script):**
```bash
# Already configured in the script:
Steps: 4 (with LoRA)
CFG: 1.0
Sampler: uni_pc
Scheduler: simple
Shift: 8.0
```

**Don't change these unless experimenting!**

### 7. Multiple Generation Attempts

**S2V has randomness - try different seeds:**

```bash
# The script uses random seeds by default, so just run multiple times
for i in {1..3}; do
  python scripts/generate_wan22_sound_video.py audio.mp3 \
    --ref-image face.jpg \
    --positive "expressive singing performance" \
    --settings "attempt_$i"
done

# Pick the best result
```

### 8. Genre-Specific Tips

#### **Ballads / Slow Songs**
✅ Works great - slower mouth movements
```bash
--positive "emotional ballad performance, slow deliberate singing, intimate expression, gentle mouth movements"
```

#### **Pop / Medium Tempo**
✅ Generally good
```bash
--positive "energetic pop performance, dynamic singing, expressive lip sync, engaging delivery"
```

#### **Rap / Fast Speech**
⚠️ Very challenging - model struggles
**Tips:**
- Use shorter clips (4-6 seconds max)
- Emphasize "rapid mouth movements" in prompt
- Lower expectations - this is a known limitation

#### **Instrumental / No Vocals**
✅ Works but differently
```bash
--positive "person reacting to music, subtle expressions, feeling the rhythm, emotional response"
# Don't mention singing/speaking if there are no vocals
```

### 9. Common Issues and Solutions

#### **Issue: Mouth barely moves**
**Solutions:**
- ✅ Use more explicit prompt: "singing with wide mouth movements"
- ✅ Try different reference image with slightly open mouth
- ✅ Check if vocals are clear in audio
- ✅ Use vocals-only track if available

#### **Issue: Movement doesn't match timing**
**Solutions:**
- ✅ Shorten duration (try 77 frames instead of 161)
- ✅ Ensure audio isn't offset (use `--audio-start` to trim silence)
- ✅ Try vocal-isolated audio track
- ✅ Generate multiple attempts

#### **Issue: Face distorts or morphs**
**Solutions:**
- ✅ Use higher quality reference image
- ✅ Reduce frame count
- ✅ Add to negative prompt: "face morphing, distortion, artifacts"
- ✅ Try different reference image angle

#### **Issue: No facial movement at all**
**Solutions:**
- ✅ Check audio has vocals (not just instrumental)
- ✅ Reference image might be too side-profile
- ✅ Increase audio prominence in mix
- ✅ Be very explicit in prompt about singing/speaking

### 10. Advanced: Custom Audio Encoder

The audio encoder (`wav2vec2_large_english_fp16.safetensors`) is optimized for English. For other languages, results may vary.

**Future improvement:** Fine-tuned audio encoders for specific languages could improve sync.

### 11. Quality Checklist

Before generating, verify:

- [ ] Reference image is high quality, well-lit, frontal face
- [ ] Audio has clear, prominent vocals
- [ ] Prompt explicitly mentions singing/speaking and mouth movements
- [ ] Duration is reasonable (under 10 seconds for best results)
- [ ] Negative prompt includes unwanted artifacts
- [ ] Ready to generate 2-3 attempts to pick best result

### 12. Example Command for Best Lip Sync

```bash
python scripts/generate_wan22_sound_video.py \
  vocals_isolated.wav \
  --ref-image professional_headshot_neutral.jpg \
  --frames 97 \
  --positive "professional singer performing into microphone, excellent lip sync to lyrics, natural expressive mouth movements, engaging eye contact, studio performance, clear enunciation, dynamic facial expressions" \
  --negative "static face, closed mouth, poor lip sync, distorted features, blurry, morphing, artifacts, unnatural movements, stiff expression"
```

## Reality Check: S2V Limitations

**What S2V does well:**
- ✅ General audio-driven motion and rhythm
- ✅ Emotional expression matching music mood
- ✅ Natural-looking facial movements
- ✅ Synchronized body language to beat

**What S2V struggles with:**
- ❌ **Perfect phoneme-level lip sync** - This is NOT a lip-sync tool like Wav2Lip
- ❌ Fast speech or rap
- ❌ Very long continuous takes (>10s)
- ❌ Multiple people with individual sync

**S2V is best for:** Music videos, performances, emotional reactions to audio - not perfect lip-syncing talking heads.

For production-quality lip sync, consider:
- Wav2Lip (phoneme-accurate but less natural)
- DID/HeyGen (commercial, better sync)
- Or accept S2V's "music video" aesthetic

## Quick Reference: Common Scenarios

| Scenario | Best Settings | Expected Quality |
|----------|--------------|------------------|
| **Ballad singer** | 97f, vocal-only, frontal portrait | ⭐⭐⭐⭐⭐ Excellent |
| **Pop performance** | 77-97f, clear audio, close-up | ⭐⭐⭐⭐ Very Good |
| **Rap/Fast speech** | 77f max, isolated vocals | ⭐⭐ Challenging |
| **Instrumental reaction** | Any length, don't mention speech | ⭐⭐⭐⭐ Good |
| **Podcast/talking** | 97f, clear speech, frontal | ⭐⭐⭐ Moderate |
| **Music video (no speech)** | Any length, describe vibe | ⭐⭐⭐⭐⭐ Excellent |

---

**Bottom line:** S2V creates compelling audio-driven videos, but it's not perfect phoneme-level lip sync. Optimize for the model's strengths: emotional expression, rhythm, and natural movement rather than frame-perfect mouth matching.

