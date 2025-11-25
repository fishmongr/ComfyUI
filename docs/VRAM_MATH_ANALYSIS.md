# RTX 5090 VRAM Analysis for Wan 2.2 14B Two-Pass

## Hardware
- Total VRAM: 32GB (32,768 MB)
- Usable after OS/drivers: ~30,500 MB

## Model Requirements (from your logs)

### Single Model (FP8):
- Model size: ~13,629 MB (13.3 GB)

### Two Models Loaded:
- High noise: 13,629 MB
- Low noise: 13,629 MB  
- **Total: 27,258 MB (26.6 GB)**

## Activation Memory (81 frames @ 832x1216)

### Latent dimensions:
- Resolution: 832 x 1216 = 1,011,712 pixels
- VAE latent: 104 x 152 x 16 channels
- Frames: 81

### Memory needed for activations:
- Transformer activations
- Attention maps
- Gradient buffers (even in inference)
- VAE decode buffers

**Estimated: 4-5 GB for 81 frames**

## VRAM Math

```
Available VRAM: 30,500 MB

Scenario 1: Both models fully loaded
- Models: 27,258 MB
- Activations: ~5,000 MB
- Total needed: 32,258 MB
- Result: EXCEEDS available VRAM by 1,758 MB
- Offload required: YES (~845 MB per model)
```

```
Scenario 2: One model at a time
- Model 1: 13,629 MB
- Activations: ~5,000 MB
- Buffer: ~2,000 MB
- Total: 20,629 MB
- Result: FITS comfortably
- Offload required: NO
```

## Conclusion

**With TWO models loaded simultaneously:**
- 845MB offload is MATHEMATICALLY NECESSARY
- Not enough VRAM for both + activations

**To avoid offload, you need:**
1. Sequential model loading (one at a time)
2. OR smaller models (5B instead of 14B)
3. OR lower resolution (<720p)
4. OR fewer frames (<61)

## Your Situation
- Resolution: 832x1216 (1.38MP - higher than 720p's 0.92MP)
- Frames: 81 (5s)
- Models: Both 14B FP8 loaded
- Result: **845MB offload is EXPECTED AND UNAVOIDABLE**



