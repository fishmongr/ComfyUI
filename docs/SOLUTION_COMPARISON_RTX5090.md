# Solution Comparison: RTX 4090/5090 Long Video Generation

## 🎯 Your Situation
- **Hardware:** RTX 5090 (32GB VRAM)
- **Models:** Wan 2.2 14B (high_noise + low_noise, two-pass)
- **Goal:** 81+ frames without offloading
- **Current:** 845MB offload with both models loaded

---

## 📊 Solution Comparison

### **Option 1: DeleteModelPassthrough (Sequential Loading)** ⭐ RECOMMENDED FOR YOU

**What it is:**
- Custom node that forcefully unloads models between passes
- Specific to your current Wan 2.2 workflow

**Pros:**
- ✅ **Works with your exact setup** (Wan 2.2 14B two-pass)
- ✅ **No workflow redesign** needed
- ✅ **Eliminates 845MB offload** 
- ✅ **Well-documented** for two-pass workflows
- ✅ **Expert-recommended** for sequential model usage

**Cons:**
- ⚠️ 10-20s overhead (model reload time)
- ⚠️ Must monitor RAM usage
- ⚠️ Requires ComfyUI restart periodically

**Expected result:**
```
Pass 1: High noise fully loaded (0 offload) - ~70s
DELETE model
Pass 2: Low noise fully loaded (0 offload) - ~70s
Total: ~150s (vs 124-137s current)
```

**Installation:**
```powershell
cd custom_nodes
git clone https://github.com/Isi-dev/ComfyUI_DeleteModelPassthrough
```

---

### **Option 2: FramePack**

**What it is:**
- Completely different architecture for video generation
- Frame compression and progressive generation
- Designed for long videos (60s+) on low VRAM (6GB)

**Compatibility with Wan 2.2:** ⚠️ **UNCLEAR**

From research:
- Primarily designed for CogVideoX, Mochi-1
- **No explicit mention** of Wan 2.2 support
- Uses different model architecture (frame packing)
- May not work with Wan's two-pass design

**Pros (if compatible):**
- ✅ Extremely efficient (6GB VRAM for 60s video)
- ✅ Designed for long videos
- ✅ No offloading issues

**Cons:**
- ❌ **Likely incompatible** with Wan 2.2 architecture
- ❌ Requires complete workflow redesign
- ❌ Different models needed
- ❌ Learning curve
- ❌ May sacrifice quality

**Verdict:** **Not recommended** - Wan 2.2 uses its own architecture that FramePack may not support

---

### **Option 3: WanVideoKsampler (ShmuelRonen)**

**What it is:**
- Custom sampler for Wan 2.1 with "intelligent memory management"
- Optimized for Wan video models specifically

**Compatibility:** ⚠️ **Wan 2.1 only** (not 2.2)

**Status:**
- Designed for Wan 2.1, not tested with 2.2
- May or may not work with 14B models
- Community reports are limited

**Verdict:** **Risky** - Not confirmed for Wan 2.2

---

### **Option 4: Accept Current Performance**

**What it is:**
- Keep 845MB offload
- 124-137s @ 81 frames

**Pros:**
- ✅ **Already working**
- ✅ **No changes needed**
- ✅ **Stable and tested**
- ✅ **Good performance** for your resolution

**Cons:**
- ❌ 845MB offload remains
- ❌ Performance degradation on 161+ frames

**Math reality:**
```
2x 14B models = 27.3GB
Activations (81f @ 832x1216) = 5GB
Total needed = 32.3GB
Available = 30.5GB
Shortfall = 1.8GB → offload required
```

---

## 🎯 **Expert Consensus for RTX 5090 + Wan 2.2**

### **For YOUR specific case (Wan 2.2 14B two-pass):**

**Primary Recommendation:** ✅ **DeleteModelPassthrough (Sequential Loading)**

**Why:**
1. **Specifically designed** for two-pass model workflows
2. **Works with Wan 2.2** (model-agnostic)
3. **Solves your exact problem** (845MB offload)
4. **Minimal workflow changes**
5. **Expert-validated approach**

**Secondary:** Accept current performance (already good for resolution)

**NOT Recommended:** FramePack (architecture incompatibility likely)

---

## 📋 **Implementation Plan**

### **Test 1: Sequential Loading** (RECOMMENDED)

1. Install DeleteModelPassthrough
2. Modify workflow:
   ```
   High Noise Model → LoRA → KSampler
         ↓
   DeleteModelPassthrough (delete high noise)
         ↓
   Low Noise Model → LoRA → KSampler
   ```
3. Test 81 frames
4. Compare: offload amount, total time, RAM usage

**Expected:**
- Offload: 0MB (both passes)
- Time: 140-160s (20s slower for reload)
- **Worth it if you want full VRAM utilization**

---

### **Test 2: Keep Current** (FALLBACK)

If sequential loading:
- Causes RAM issues
- Is significantly slower
- Doesn't eliminate offload

**Fallback:** Your current 124-137s with 845MB offload is **already excellent** for:
- 832x1216 (54% more pixels than OpenArt's benchmark)
- Two-pass high-quality workflow
- 81 frames

---

## ✅ **Final Recommendation**

**For RTX 5090 + Wan 2.2 14B long videos:**

1. **Try DeleteModelPassthrough first** - It's the expert-recommended solution for your exact use case
2. **If that doesn't work well** - Accept your current performance (it's already good!)
3. **Don't use FramePack** - Architecture mismatch with Wan 2.2

**Your current 124-137s @ 81 frames is already optimal for your hardware/workflow combo if sequential loading doesn't help.**

---

## 🚀 **Next Step**

Want me to:
1. ✅ Install DeleteModelPassthrough and test? (Recommended)
2. ⏸️ Document current performance as optimized baseline?
3. 🔍 Research FramePack compatibility more deeply?

**My vote:** Option 1 - Let's try sequential loading! If it eliminates offload, that's a win. If not, your current setup is already excellent.



