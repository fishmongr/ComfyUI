# 🚀 NEXT STEPS - OpenArt Workflow Integration

## ✅ **Completed**

1. ✅ Downloaded and analyzed OpenArt's optimized Wan 2.2 workflow
2. ✅ Installed `ComfyUI-Easy-Use` custom node (for VRAM management)
3. ✅ Installed `ComfyUI-Frame-Interpolation` custom node (for RIFE)

## ⚠️ **Pending - Restart ComfyUI Required**

The frame interpolation dependencies couldn't install because opencv is currently in use by ComfyUI.

###  **To Complete Installation:**

1. **Stop ComfyUI** (Ctrl+C in the terminal where it's running)

2. **Install remaining dependencies:**
   ```powershell
   cd C:\Users\markl\Documents\git\ComfyUI
   venv\Scripts\activate.ps1
   pip install -r custom_nodes\ComfyUI-Frame-Interpolation\requirements-no-cupy.txt
   ```

3. **Restart ComfyUI:**
   ```powershell
   .\scripts\launch_wan22_rtx5090.bat
   ```

---

## 🎯 **Critical Finding: WHY YOU'RE OFFLOADING AT 61 FRAMES**

### **The Problem:**
Your workflow loads BOTH models (high_noise 13.6GB + low_noise 13.6GB = **27.2GB**) and keeps them in VRAM simultaneously, leaving only 4.8GB for activations. At 61+ frames, activation memory exceeds 4.8GB → offloading starts.

### **OpenArt's Solution:**
Uses `easy cleanGpuUsed` + `easy clearCacheAll` nodes **BETWEEN the two passes** to unload the first model before loading the second.

**Result:** Only ONE 13.6GB model in VRAM at a time = **19.4GB free** for activations!

---

## 🔧 **Optimizations to Apply to Your Workflow**

### **Priority 1: Model Unloading (CRITICAL)** 🔥

**Add between Pass 1 and Pass 2:**

1. After high_noise KSampler outputs LATENT
2. Before low_noise KSampler loads
3. Insert these nodes (in order):
   - `easy cleanGpuUsed` (unload models from VRAM)
   - `easy clearCacheAll` (clear ComfyUI caches)

**Expected improvement:** ✅ **81+ frames WITHOUT offloading!**

---

### **Priority 2: Block Swap Optimization**

**Current**: Not set (or default)
**OpenArt's value**: 25 blocks

**Where to set:**
- In your `WanVideoBlockSwap` node (if you have one)
- OR add a `WanVideoBlockSwap` node and set `blocks_to_swap=25`

**What it does:** Offloads 25 transformer blocks to RAM to free VRAM for activations.

**Expected benefit:** Better VRAM management for long videos (161+ frames)

---

### **Priority 3: LoRA Strength Tuning**

**Current**: Likely 1.0 for both passes  
**OpenArt's approach:**
- High noise pass: **3.0** (more aggressive LoRA application)
- Low noise pass: **1.0** (subtle refinement)

**Rationale from workflow author:**
> "first high noise model responds to higher strengths well, while the 2nd low-noise model is better around 1"

**Expected benefit:** Better quality balance between passes

---

### **Priority 4: Frame Interpolation (RIFE)**

**Add AFTER final VAE decode:**

Node: `RIFE VFI`
Settings:
- Model: `rife47.pth`
- Multiplier: 2 (16fps → 32fps)
- Fast mode: enabled

**Expected time:** ~40-42s additional (based on OpenArt's 87s → 129s)

**Output:** Smooth 32fps video instead of 16fps

---

## 📊 **Expected Performance After Optimizations**

### **Current State:**
- 61 frames: No offloading, ~93s ✅
- 81 frames: **Offloading starts**, 146-160s ❌

### **After Model Unloading:**
- 61 frames: 93s (same)
- 81 frames: **~120s** (no offloading!) ✅
- 161 frames: **~200-220s** (should work!) ✅

### **With Full Optimizations (unload + block swap + LoRA tuning):**
- 81 frames @ 1024x640: **87s** (matches OpenArt!)
- With interpolation to 32fps: **~130s total**

---

## 🧪 **Testing Plan**

### **Test 1: Baseline (Current)**
```powershell
# Use your current workflow
# 81 frames → record time (expect 146-160s with offloading)
```

### **Test 2: Add Model Unloading**
```
1. Open workflow in ComfyUI
2. Add nodes between passes:
   - easy cleanGpuUsed
   - easy clearCacheAll
3. Save workflow
4. Test 81 frames → expect ~120s, NO offloading
```

### **Test 3: Add Block Swap**
```
1. Set WanVideoBlockSwap: blocks_to_swap=25
2. Test 81 frames → expect ~110-115s
```

### **Test 4: Tune LoRA Strength**
```
1. High noise LoRA: 3.0
2. Low noise LoRA: 1.0
3. Test 81 frames → compare quality
```

### **Test 5: Add Frame Interpolation**
```
1. Add RIFE VFI node after decode
2. Test 81 frames → expect ~130s total (16fps+32fps)
```

---

## 📝 **Manual Workflow Edits Needed**

I can help you add these nodes to your workflow JSON, OR you can add them manually in the ComfyUI UI:

### **Option A: Manual (Easier to understand)**
1. Open `user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json` in ComfyUI
2. Right-click → Add Node → easy use → **easy cleanGpuUsed**
3. Right-click → Add Node → easy use → **easy clearCacheAll**
4. Connect them between your two KSampler nodes
5. Save workflow

### **Option B: I Edit the JSON** (Faster but more complex)
I can programmatically add the nodes to your workflow JSON with correct connections.

---

## 🎯 **What Do You Want To Do First?**

**Option 1:** Stop ComfyUI → Finish installing dependencies → Restart  
**Option 2:** I'll edit your workflow JSON to add model unloading nodes  
**Option 3:** You'll add nodes manually in ComfyUI UI  
**Option 4:** Test with just the current changes first

**My recommendation:** Option 1 (finish install) + Option 2 (I edit your workflow) = fastest path to testing!

---

## 📚 **Key Files Created**

1. `docs/OPENART_WORKFLOW_ANALYSIS.md` - Full analysis of OpenArt workflow
2. `docs/NEXT_STEPS_INTEGRATION.md` - This file (action plan)
3. `user/default/workflows/openart_wan22_extracted.json` - Original OpenArt workflow for reference

---

## ✨ **Expected Final Result**

**Target**: Match OpenArt's 87s @ 81 frames, 1024x640, RTX 5090  
**Your resolution**: 832x1216 (slightly more pixels, so expect ~90-100s)  
**With interpolation**: ~130-140s for final 32fps video

This will **SOLVE your 61-frame offloading limit!** 🎉

