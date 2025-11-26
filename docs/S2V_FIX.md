# S2V Fixed - Type Mismatch Resolved ✅

## Issue

Initial workflow had incorrect node connections causing validation error:

```
Failed to validate prompt for output 108:
* WanSoundImageToVideo 98:
  - Return type mismatch: received AUDIO_ENCODER, expected AUDIO_ENCODER_OUTPUT
```

## Root Cause

**Missing audio encoding step!**

❌ **Original (incorrect):**
```
Node 119: LoadAudio → AUDIO
Node 120: AudioEncoderLoader → AUDIO_ENCODER
Node 98: WanSoundImageToVideo ← Connected to 120 (wrong type!)
```

✅ **Fixed:**
```
Node 119: LoadAudio → AUDIO
Node 120: AudioEncoderLoader → AUDIO_ENCODER (model)
Node 122: AudioEncoderEncode → AUDIO_ENCODER_OUTPUT (encoded audio)
Node 98: WanSoundImageToVideo ← Connected to 122 (correct type!)
```

## Solution

Added **`AudioEncoderEncode` node (122)** to actually encode the audio:

```json
"122": {
  "inputs": {
    "audio_encoder": ["120", 0],  // Audio encoder model
    "audio": ["119", 0]            // Raw audio data
  },
  "class_type": "AudioEncoderEncode",
  "_meta": {
    "title": "Encode Audio"
  }
}
```

Then updated node 98 to use the encoded output:

```json
"98": {
  "inputs": {
    // ... other inputs ...
    "audio_encoder_output": ["122", 0]  // Now correct type!
  }
}
```

## Validation

```bash
python scripts/test_s2v_workflow.py
```

**Results:**
```
✅ ALL TESTS PASSED

Audio pipeline:
  - Node 119: LoadAudio → AUDIO
  - Node 120: AudioEncoderLoader → AUDIO_ENCODER
  - Node 122: AudioEncoderEncode → AUDIO_ENCODER_OUTPUT
  - Node 98: WanSoundImageToVideo (uses encoded audio)
```

## Files Updated

- ✅ `scripts/last_prompt_api_format_s2v.json` - Added node 122, fixed connections
- ✅ `scripts/generate_wan22_sound_video.py` - Updated to use node 122 for trimming
- ✅ `scripts/test_s2v_workflow.py` - Validates correct audio pipeline

## Ready to Test!

The type mismatch is resolved. Try the script now:

```bash
python scripts/generate_wan22_sound_video.py input/your-audio.mp3
```

Should work correctly now! 🎵✅

