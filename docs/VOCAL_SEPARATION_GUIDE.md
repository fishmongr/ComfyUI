# Vocal Separation Guide for S2V

## Why Separate Vocals?

**Isolated vocals dramatically improve S2V lip sync quality:**
- ✅ Clearer audio signal for Wav2Vec2 encoder
- ✅ No instrumental masking the vocals
- ✅ Better temporal feature extraction
- ✅ More consistent mouth movements
- ✅ Stronger audio-visual correlation

**Before/After:**
- ❌ Full mix: Drums, bass, guitar + vocals = noisy signal
- ✅ Vocals only: Clean vocal track = clear features

---

## Method 1: Demucs (Meta/Facebook) - RECOMMENDED

**Best quality, Python-based, state-of-the-art separation**

### Installation

```bash
# In ComfyUI venv
cd C:\Users\markl\Documents\git\ComfyUI
venv\Scripts\activate

pip install demucs
```

### Basic Usage

```bash
# Best quality model (htdemucs_ft - fine-tuned)
demucs --two-stems vocals -o "input/vocals" "path/to/audio.mp3"

# Faster model (htdemucs)
demucs -n htdemucs --two-stems vocals -o "input/vocals" "audio.mp3"

# Highest quality (slower, 6-source model)
demucs -n htdemucs_6s --two-stems vocals -o "input/vocals" "audio.mp3"
```

### Output Structure

```
input/vocals/htdemucs_ft/song_name/
├── vocals.wav      ← USE THIS
└── no_vocals.wav
```

### Python API Usage

```python
import torch
import torchaudio
from demucs.pretrained import get_model
from demucs.apply import apply_model

# Load model
model = get_model('htdemucs_ft')
model.cpu()
model.eval()

# Load audio
wav, sr = torchaudio.load("audio.mp3")

# Separate
with torch.no_grad():
    sources = apply_model(model, wav[None])

# sources: [batch, source, channel, time]
# source order: drums, bass, other, vocals
vocals = sources[0, 3]  # Get vocals

# Save
torchaudio.save("vocals.wav", vocals, sr)
```

### Batch Processing Multiple Songs

```python
# scripts/batch_separate_vocals.py
from pathlib import Path
import subprocess
import sys

def separate_vocals(audio_path, output_dir="input/vocals"):
    """Separate vocals using Demucs."""
    cmd = [
        "demucs",
        "--two-stems", "vocals",
        "-o", output_dir,
        str(audio_path)
    ]
    subprocess.run(cmd, check=True)
    
    # Return path to vocals
    audio_name = Path(audio_path).stem
    return Path(output_dir) / "htdemucs_ft" / audio_name / "vocals.wav"

if __name__ == "__main__":
    audio_files = Path("input").glob("*.mp3")
    for audio in audio_files:
        print(f"Processing: {audio.name}")
        vocal_path = separate_vocals(audio)
        print(f"Vocals saved: {vocal_path}")
```

---

## Method 2: Spleeter (Deezer) - FAST ALTERNATIVE

**Good for quick tests, slightly lower quality than Demucs**

### Installation

```bash
cd C:\Users\markl\Documents\git\ComfyUI
venv\Scripts\activate

pip install spleeter
```

### Usage

```bash
# 2-stem separation (vocals + accompaniment)
spleeter separate -p spleeter:2stems -o "input/vocals" "path/to/audio.mp3"

# 4-stem separation (vocals, bass, drums, other)
spleeter separate -p spleeter:4stems -o "input/vocals" "path/to/audio.mp3"
```

### Output Structure

```
input/vocals/song_name/
├── vocals.wav      ← USE THIS
└── accompaniment.wav
```

### Python API Usage

```python
from spleeter.separator import Separator

# Initialize separator
separator = Separator('spleeter:2stems')

# Separate
separator.separate_to_file(
    "audio.mp3",
    destination="input/vocals/"
)

# Vocals saved to: input/vocals/audio/vocals.wav
```

---

## Method 3: Audio Separator (OpenUnmix + More)

**Unified interface for multiple models**

### Installation

```bash
pip install audio-separator
```

### Usage

```bash
# Using Demucs through audio-separator
audio-separator "audio.mp3" --model_name htdemucs_ft

# Using MDX models
audio-separator "audio.mp3" --model_name UVR-MDX-NET-Voc_FT
```

### Python API

```python
from audio_separator.separator import Separator

separator = Separator(model_file_dir='models/')
separator.load_model(model_filename='htdemucs_ft.yaml')

output_files = separator.separate("audio.mp3")
# Returns: ['vocals.wav', 'accompaniment.wav']
```

---

## Comparison Table

| Tool | Quality | Speed | Ease of Use | GPU Support |
|------|---------|-------|-------------|-------------|
| **Demucs** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Yes |
| **Spleeter** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Yes |
| **Audio Separator** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Yes |

**Recommendation:** Use **Demucs** for best quality

---

## Integrated S2V + Vocal Separation Script


```python
# scripts/s2v_with_vocal_separation.py
import subprocess
import sys
from pathlib import Path

def separate_vocals_demucs(audio_path, output_dir="input/vocals"):
    """Separate vocals using Demucs (best quality)."""
    print(f"\n{'='*70}")
    print(f"Separating vocals with Demucs...")
    print(f"{'='*70}")
    
    cmd = [
        "demucs",
        "--two-stems", "vocals",
        "-o", output_dir,
        str(audio_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    # Find output vocal file
    audio_name = Path(audio_path).stem
    vocal_file = Path(output_dir) / "htdemucs_ft" / audio_name / "vocals.wav"
    
    if not vocal_file.exists():
        # Try alternative path structure
        vocal_file = Path(output_dir) / "htdemucs" / audio_name / "vocals.wav"
    
    if not vocal_file.exists():
        print(f"Error: Could not find vocal output at {vocal_file}")
        sys.exit(1)
    
    print(f"✓ Vocals extracted: {vocal_file}")
    return vocal_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python s2v_with_vocal_separation.py audio_file [--ref-image IMAGE] [--frames N] [...]")
        print("\nExample:")
        print("  python s2v_with_vocal_separation.py song.mp3 --ref-image face.jpg --frames 97")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    # Step 1: Separate vocals
    vocal_file = separate_vocals_demucs(audio_path)
    
    # Step 2: Generate S2V with vocals
    s2v_cmd = [
        sys.executable,
        "scripts/generate_wan22_sound_video.py",
        str(vocal_file)
    ] + sys.argv[2:]  # Pass through all other arguments
    
    print(f"\n{'='*70}")
    print("Generating S2V video with isolated vocals...")
    print(f"{'='*70}\n")
    
    subprocess.run(s2v_cmd, check=True)

if __name__ == "__main__":
    main()
```

### Usage

```bash
# Automatic: Separate vocals + generate S2V in one command
python scripts/s2v_with_vocal_separation.py "input/song.mp3" \
  --ref-image input/face.jpg \
  --frames 97 \
  --positive "woman singing passionately" \
  --interpolate film
```

---

## Quick Start Guide (Python-Only Workflow)

### 1. Install Demucs

```bash
cd C:\Users\markl\Documents\git\ComfyUI
venv\Scripts\activate

pip install demucs
```

### 2. Test Vocal Separation

```bash
# Quick test
demucs --two-stems vocals -o "input/vocals" "input/your-song.mp3"

# Check output
dir "input\vocals\htdemucs_ft\your-song\"
# Should see: vocals.wav and no_vocals.wav
```

### 3. Generate S2V with Vocals

```bash
python scripts/generate_wan22_sound_video.py ^
  "input/vocals/htdemucs_ft/your-song/vocals.wav" ^
  --ref-image input/face.jpg ^
  --frames 97 ^
  --positive "woman singing passionately, clear lip movements" ^
  --interpolate film
```

### 4. Or Use the Integrated Script

```bash
# One-command workflow
python scripts/s2v_with_vocal_separation.py "input/song.mp3" ^
  --ref-image input/face.jpg ^
  --frames 97 ^
  --interpolate film
```

### Compare Results

**With full mix:**
- Mixed instruments mask vocals
- Noisy audio features
- Inconsistent lip movements

**With isolated vocals:**
- Clean vocal signal
- Clear audio features
- Better lip sync (30-50% improvement)
- More consistent results

---

## Advanced Usage

### Demucs Model Options

```bash
# Default (htdemucs_ft) - Best balance
demucs --two-stems vocals "audio.mp3"

# Fastest (htdemucs)
demucs -n htdemucs --two-stems vocals "audio.mp3"

# Highest quality (htdemucs_6s) - Slower
demucs -n htdemucs_6s --two-stems vocals "audio.mp3"

# Use CPU if GPU has issues
demucs --device cpu --two-stems vocals "audio.mp3"
```

### Custom Output Location

```bash
demucs --two-stems vocals \
  -o "D:\MyProject\vocals" \
  "input/song.mp3"
```

### Process Multiple Files

```python
# scripts/batch_vocal_separation.py
from pathlib import Path
import subprocess

input_dir = Path("input")
audio_files = list(input_dir.glob("*.mp3")) + list(input_dir.glob("*.m4a"))

for audio in audio_files:
    print(f"Processing: {audio.name}")
    subprocess.run([
        "demucs",
        "--two-stems", "vocals",
        "-o", "input/vocals",
        str(audio)
    ])
    print(f"✓ Done: {audio.stem}")
```

---

## Performance Tips

### GPU Acceleration
Demucs automatically uses GPU if available. Check with:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0)}")
```

### Speed vs Quality Trade-offs

| Model | Quality | Speed | VRAM | Use Case |
|-------|---------|-------|------|----------|
| `htdemucs` | ⭐⭐⭐⭐ | Fast | ~2GB | Quick tests |
| `htdemucs_ft` | ⭐⭐⭐⭐⭐ | Medium | ~3GB | **Recommended** |
| `htdemucs_6s` | ⭐⭐⭐⭐⭐ | Slow | ~4GB | Best quality |

### Memory Issues?
```bash
# Use CPU instead of GPU
demucs --device cpu --two-stems vocals "audio.mp3"

# Or use Spleeter (lighter)
pip install spleeter
spleeter separate -p spleeter:2stems -o vocals "audio.mp3"
```

---

## Troubleshooting

**Issue: `demucs: command not found`**
- Solution: Activate venv first: `venv\Scripts\activate`
- Or use: `python -m demucs ...`

**Issue: Out of memory error**
- Solution: Use CPU mode: `demucs --device cpu ...`
- Or use lighter Spleeter: `pip install spleeter`

**Issue: Vocals sound "phasey" or artifacts**
- Solution: Try different model: `demucs -n htdemucs_6s ...`
- Normal with complex mixes - some artifacts expected

**Issue: Separation is slow**
- Solution: Use GPU (automatic if available)
- Or use faster model: `demucs -n htdemucs ...`
- Or try Spleeter for speed over quality

**Issue: Can't find output file**
- Check: `input/vocals/htdemucs_ft/song-name/vocals.wav`
- Or: `input/vocals/htdemucs/song-name/vocals.wav`
- Model name varies based on which you used

---

## Post-Processing (Optional)

### Normalize Volume

```bash
# If vocals are too quiet
ffmpeg -i vocals.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" vocals_normalized.wav
```

### Remove Silence

```bash
# Trim silence from start/end
ffmpeg -i vocals.wav -af "silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB" vocals_trimmed.wav
```

### Convert Format

```bash
# Convert to different format if needed
ffmpeg -i vocals.wav -c:a libmp3lame -b:a 320k vocals.mp3
```

---

## Complete Workflow Example

```bash
# 1. Install Demucs (one-time)
cd C:\Users\markl\Documents\git\ComfyUI
venv\Scripts\activate
pip install demucs

# 2. Separate vocals
demucs --two-stems vocals -o "input/vocals" "input/song.mp3"

# 3. Generate S2V with clean vocals
python scripts/generate_wan22_sound_video.py ^
  "input/vocals/htdemucs_ft/song/vocals.wav" ^
  --ref-image input/face.jpg ^
  --frames 97 ^
  --positive "expressive singing, clear lip movements" ^
  --interpolate film

# Or use the integrated script for one command:
python scripts/s2v_with_vocal_separation.py "input/song.mp3" ^
  --ref-image input/face.jpg ^
  --frames 97 ^
  --interpolate film
```

**Expected improvement:** 30-50% better lip sync consistency! 🎵🎤

