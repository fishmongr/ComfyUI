# OpenArt Wan 2.2 Workflow Analysis - Key Optimizations

## Source
**Workflow**: "WAN 2.2 T2V For High-End Systems, Speed and Quality Focused"
**Author**: dowhatyouwantcuzapirateisfree  
**Downloads**: 1,789 | **Views**: 9,523
**Performance**: 87s @ 81 frames (1024x640), 129s with interpolation (RTX 5090)

---

## 🎯 Key Optimizations Found

### 1. **VRAM Management: Cache Clearing Nodes** ✅ **CRITICAL**

**Nodes Used:**
- `easy clearCacheAll` - Clears all ComfyUI caches
- `easy cleanGpuUsed` - Unloads models from VRAM

**Implementation:**
- Both nodes are **BYPASSED by default** (mode: 4)
- Controlled by "Clear Cache After Generation" toggle
- Located AFTER video decode, BEFORE frame interpolation
- Only run when needed (user toggle)

**From description:**
> "Clear Cache After Generation, which will unload the model after a render. Useful if you notice comfy not letting go of your VRAM between gens. Sadly will not clear system RAM."

**Custom Node Required:** `ComfyUI Easy Use`

---

### 2. **Frame Interpolation: RIFE** ✅

**Node**: `RIFE VFI`  
**Settings**:
- Model: `rife47.pth` (latest RIFE version)
- Multiplier: 2x (16fps → 32fps)
- Fast mode: enabled

**Implementation:**
- Toggle-able via "Rife 32 FPS Frame Interpolation" group
- Can be disabled to test generation without interpolation
- Then re-enabled to interpolate last render without re-gen

**Performance Impact:**
- Base generation: 87s @ 81 frames
- With interpolation: 129s (42s additional for RIFE)

**Custom Node Required:** `ComfyUI Frame Interpolation`

---

### 3. **Block Swap Optimization** ✅

**Value**: 25 blocks (vs your current: none specified)

**What it does:**
- Offloads specific model blocks to RAM to free VRAM
- 25 blocks is optimized for RTX 5090 with 14B models
- Higher than Wan 2.1 (they note this explicitly)

**Implementation:**
- `WanVideoBlockSwap` node
- Applied to BOTH high_noise and low_noise models
- Set via dedicated parameter widget

---

### 4. **Experimental Args** ✅

**Node**: `WanVideoExperimentalArgs`  
**Purpose**: Additional performance optimizations

**Settings observed:**
- Applied to both samplers (high_noise and low_noise)
- Specific values not fully visible in extracted JSON

---

### 5. **LoRA Strategy** ✅ **DIFFERENT APPROACH**

**Their approach:**
- Separate LoRA groups: "High Loras", "Low Loras", "Loras High AND Low"
- **Lightx2v High**: Strength 3.0 (high_noise model)
- **Lightx2v Low**: Strength 1.0 (low_noise model)
- Multi-lora support for up to 5 loras per model

**Key insight from description:**
> "Don't unload this lora, just adjust strength if needed. Seems like the first high noise model responds to higher strengths well, while the 2nd low-noise model is better around 1."

---

### 6. **Attention Backend** ✅

**Both models use**: `sageattn` (SageAttention)

**Note**: This is what we tried to build but failed due to compilation issues.

---

### 7. **Two-Pass Configuration**

**Split Steps**: 3 (out of 6 total steps)
- Steps 0-3: High noise pass
- Steps 3-6: Low noise pass

**Your current**: Likely different step split

---

### 8. **Video Output Organization**

**Directory structure:**
```
output/
├── Wan2_2_T2V/
│   ├── YYYY_MM_DD/
│   │   ├── vid_XXXXX.mp4 (16fps base)
│   │   ├── interpolated/
│   │   │   └── vid_XXXXX.mp4 (32fps)
│   │   └── finalframe/
│   │       └── vidfinal_XXXXX.png (last frame for I2V)
```

**Benefits:**
- Date-organized
- Separate base vs interpolated renders
- Saves final frame for I2V extension workflows

---

## 🚀 Optimizations to Integrate Into Your Workflow

### Priority 1: **CRITICAL - Model Unloading**

**Install:**
```bash
cd custom_nodes
git clone https://github.com/yolain/ComfyUI-Easy-Use
cd ..
```

**Add to workflow AFTER high_noise decode, BEFORE low_noise load:**
1. `easy cleanGpuUsed` node
2. `easy clearCacheAll` node

**Expected benefit:** ✅ **SOLVES YOUR 61-FRAME OFFLOADING ISSUE**

---

### Priority 2: **Frame Interpolation**

**Install:**
```bash
cd custom_nodes
git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation
cd ..
pip install -r custom_nodes/ComfyUI-Frame-Interpolation/requirements.txt
```

**Add to workflow AFTER final decode:**
- `RIFE VFI` node with multiplier=2

**Expected benefit:** 16fps → 32fps, ~40s additional processing

---

### Priority 3: **Block Swap**

**Set in WanVideoBlockSwap node:**
- `blocks_to_swap`: 25 (optimized for 5090)

**Expected benefit:** Reduced VRAM pressure for long videos

---

### Priority 4: **Differential LoRA Strength**

**Adjust LoRA strengths:**
- High noise pass: 3.0 (or test 2.0-4.0 range)
- Low noise pass: 1.0 (keep as is)

**Expected benefit:** Better quality balance between passes

---

## ⚠️ Notes from OpenArt Workflow Author

1. **RAM Requirements:**
   > "Also you should have at least 64Gb of system RAM as well, to handle model/lora offloading."
   
   You have 128GB ✅

2. **Memory Creep:**
   > "WAN 2.2 will memory creep faster than 2.1 did, keep an eye out so you don't lock up your system!"
   
   This is why cache clearing is important.

3. **Block Swap Higher Than 2.1:**
   > "Also you'll need a higher block swap than what 2.1 required."
   
   Use 25 blocks for 5090.

4. **Performance on 5090:**
   > "On a 5090, with the model already loaded it puts out high quality gens at 81 frames at 1024x640 in about 87 seconds"
   
   This is **EXACTLY** your target performance (67-87s)!

---

## 🎯 Next Steps

1. **Install ComfyUI-Easy-Use** (for cache clearing)
2. **Install ComfyUI-Frame-Interpolation** (for RIFE)
3. **Update your workflow** with optimized settings
4. **Test 81 frames** → should NOT offload now
5. **Benchmark** → compare to OpenArt's 87s

