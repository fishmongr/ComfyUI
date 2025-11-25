# TaylorSeer Analysis: Should It Work with RTX 5090 & WAN2.2?

## **✅ Official Evidence: It SHOULD Work**

### **From TaylorSeer README.md:**

> "**Exciting Performance on WAN 2.2**: For 81 frames generation on RTX 5090, TaylorSeer-Lite achieves remarkable acceleration - **386s vs 1176s** (3.05x speedup) compared to the original implementation!"

**Key Facts:**
- ✅ **RTX 5090 is officially supported** - explicitly mentioned in README
- ✅ **WAN 2.2 is supported** - dedicated example workflow included
- ✅ **Performance benchmark published** - 386s vs 1176s (3.05x speedup)
- ✅ **Last update:** September 25, 2025 - very recent

---

## **📊 Official Example Workflow Analysis**

### **Official Example: `taylorseerlite_example_wan2-2.json`**

**Key Configuration:**

```json
"125": {  // TaylorSeer for HIGH NOISE model
  "inputs": {
    "model_type": "wanvideo",
    "fresh_threshold": 5,
    "max_order": 1,
    "first_enhance": 1,
    "last_enhance": 50,
    "model": ["37", 0]  // DIRECTLY from UNETLoader
  },
  "class_type": "TaylorSeerLite"
}

"126": {  // TaylorSeer for LOW NOISE model
  "inputs": {
    "model_type": "wanvideo",
    "fresh_threshold": 5,
    "max_order": 1,
    "first_enhance": 1,
    "last_enhance": 50,
    "model": ["56", 0]  // DIRECTLY from UNETLoader
  },
  "class_type": "TaylorSeerLite"
}
```

**Flow:**
```
UNETLoader (37 - high noise) → TaylorSeerLite (125) → ModelSamplingSD3 (54) → KSampler
UNETLoader (56 - low noise) → TaylorSeerLite (126) → ModelSamplingSD3 (55) → KSampler
```

**Key Details:**
- ✅ Resolution: 720x1280 (official example)
- ✅ Frames: 81 
- ✅ Steps: 20 (split: 0-10 high noise, 10-20 low noise)
- ✅ NO LoRA nodes in the official example
- ✅ TaylorSeer connects DIRECTLY from UNET → ModelSampling

---

## **🔍 Your Workflow (Likely Structure)**

Based on your error messages and documentation references:

```
UNETLoader (95 - high noise) → LoRA (101) → TaylorSeer (119/121) → ModelSampling (104) → KSampler
UNETLoader (96 - low noise) → LoRA (102) → TaylorSeer (120/122) → ModelSampling (103) → KSampler
```

**Key Differences:**
- ❌ You have LoRA nodes BEFORE TaylorSeer
- ❌ Resolution: 832x1216 (vs official 720x1280)
- ❌ Steps: 4 (vs official 20)
- ✅ Same TaylorSeer settings (model_type, thresholds, etc.)

---

## **🚨 CRITICAL ISSUE IDENTIFIED**

### **LoRA + TaylorSeer Interaction**

**The Problem:**
1. **LoRA modifies the model** with weight patches
2. **TaylorSeer expects a clean, unmodified model**
3. **Model cloning** happens: `new_model = model.clone()` (line 301 in TaylorSeer)
4. **When LoRA + TaylorSeer clone together**, CUDA state gets corrupted

**Evidence:**
- Official example has **NO LoRA** nodes
- Your workflow has **LoRA BEFORE TaylorSeer**
- Error happens during **model unloading** (when LoRA patches are being removed)

---

## **💡 SOLUTION: Change Node Order**

### **Option 1: Move LoRA AFTER TaylorSeer (Recommended)**

**New Flow:**
```
UNETLoader → TaylorSeer → LoRA → ModelSampling → KSampler
```

**Why This Works:**
- TaylorSeer gets clean, unpatched model
- LoRA applies after TaylorSeer's caching is set up
- No CUDA state conflict during unloading

### **Option 2: Remove LoRA When Using TaylorSeer**

**New Flow:**
```
UNETLoader → TaylorSeer → ModelSampling → KSampler
```

**Why This Works:**
- Matches official example exactly
- No LoRA complications
- Clean TaylorSeer operation

### **Option 3: Use LoRA WITHOUT TaylorSeer**

**Your Current Working Flow:**
```
UNETLoader → LoRA → ModelSampling → KSampler
```

**Keep using this if you need the LoRA.**

---

## **📝 Step-by-Step Fix**

### **Test 1: Official Example (Verify TaylorSeer Works)**

1. **Load the official example:**
   ```
   custom_nodes/ComfyUI-TaylorSeer/examples/taylorseerlite_example_wan2-2.json
   ```

2. **Run it with your models**
   - Use your WAN2.2 models
   - Should complete WITHOUT errors
   - Time: ~386 seconds for 81 frames

**If this works:** TaylorSeer + RTX 5090 is fine, the issue is your workflow structure

**If this fails:** TaylorSeer has compatibility issues with your setup

### **Test 2: Modify Your Workflow (Remove LoRA)**

1. **Open:** `video_wan2_2_14B_i2v_TAYLORSEER.json`
2. **Delete LoRA nodes** (101, 102)
3. **Reconnect:**
   - `UNET 95 → TaylorSeer 119/121 → ModelSampling 104`
   - `UNET 96 → TaylorSeer 120/122 → ModelSampling 103`
4. **Save as NEW file:** `video_wan2_2_14B_i2v_TAYLORSEER_NO_LORA.json`
5. **Test**

**Expected:** Should work without CUDA errors

### **Test 3: LoRA After TaylorSeer (If You Need LoRA)**

1. **Open your workflow**
2. **Reorder nodes:**
   - `UNET 95 → TaylorSeer 119 → LoRA 101 → ModelSampling 104`
   - `UNET 96 → TaylorSeer 120 → LoRA 102 → ModelSampling 103`
3. **Save as NEW file:** `video_wan2_2_14B_i2v_TAYLORSEER_LORA_AFTER.json`
4. **Test**

**Expected:** May or may not work (LoRA after caching is unusual)

---

## **🔧 Additional Compatibility Notes**

### **ComfyUI Version Requirement**

From README:
> "Please ensure your ComfyUI version is newer than commit `c496e53`."

**Check your version:**
```powershell
cd C:\Users\markl\Documents\git\ComfyUI
git log --oneline -1
```

If it's older than `c496e53`, update ComfyUI:
```powershell
git pull
```

### **Resolution Differences**

- **Official example:** 720x1280 (0.9M pixels, 81 frames)
- **Your workflow:** 832x1216 (1.0M pixels, 81 frames)
- **VRAM impact:** ~11% higher

This shouldn't cause CUDA errors, but might affect memory management.

### **Steps Configuration**

- **Official:** 20 steps (10 high noise, 10 low noise)
- **Your workflow:** 4 steps total

**With only 4 steps:**
- `first_enhance: 1` means full computation on step 0
- `last_enhance: 50` is irrelevant (only 4 steps total)
- TaylorSeer caching barely activates

**Recommendation:** With 4 steps, TaylorSeer might not provide much benefit. It's designed for 20-50 step workflows.

---

## **🎯 Most Likely Issue: LoRA + TaylorSeer Conflict**

### **Why This Causes CUDA Errors:**

1. **LoRA patches the model** in VRAM
2. **TaylorSeer clones the patched model**
3. **TaylorSeer adds its own patches** (hooks, caching)
4. **During unloading:**
   - ComfyUI tries to unpatch LoRA
   - TaylorSeer's patches are still active
   - **CUDA state becomes inconsistent**
   - **Error: "invalid argument"**

### **The Fix:**

Either:
- ✅ **Remove LoRA** (like official example)
- ✅ **Move LoRA after TaylorSeer** (untested, may work)
- ✅ **Don't use TaylorSeer** (stick with working workflow)

---

## **📊 Performance Expectations**

### **With TaylorSeer (No LoRA):**
- **Official benchmark:** 386s for 81 frames @ 720x1280
- **Your resolution:** 832x1216 (11% higher)
- **Expected:** ~430s for 81 frames
- **vs Without TaylorSeer:** ~125-137s... **WAIT, WHAT?**

### **⚠️ MAJOR DISCREPANCY DETECTED**

**Official TaylorSeer benchmark:**
- **Without TaylorSeer:** 1176s for 81 frames
- **With TaylorSeer:** 386s (3.05x speedup)

**Your current performance:**
- **Without TaylorSeer:** ~125-137s for 81 frames
- **Expected with TaylorSeer:** ~40-50s

**This doesn't match!** Your baseline (125s) is **9.4x faster** than the official baseline (1176s).

**Possible explanations:**
1. **Your 4-step workflow** vs official 20-step workflow (5x speedup)
2. **Your optimizations** (FP8, no SageAttention, memory management)
3. **Different hardware** (though both use RTX 5090)

**Conclusion:** TaylorSeer is designed for **longer sampling runs (20-50 steps)**. With only **4 steps**, the caching overhead might actually SLOW YOU DOWN.

---

## **🎯 Final Recommendations**

### **Recommendation 1: Test Official Example (Highest Priority)**

Load and run: `custom_nodes/ComfyUI-TaylorSeer/examples/taylorseerlite_example_wan2-2.json`

**If it works:** Problem is your workflow structure (likely LoRA conflict)  
**If it fails:** TaylorSeer has deeper issues with your setup

### **Recommendation 2: Remove LoRA from TaylorSeer Workflow**

Your LoRA nodes are likely causing the CUDA conflict. Official example has none.

### **Recommendation 3: Consider TaylorSeer May Not Help You**

With **4 steps**, TaylorSeer's caching has minimal time to activate:
- Step 0: Full computation (first_enhance)
- Steps 1-3: Minimal caching benefit

**Your current 125s workflow might be optimal** for 4-step generation.

---

## **✅ Action Plan**

1. **Test official TaylorSeer example** (30 min)
   - Confirms if TaylorSeer + RTX 5090 works at all

2. **If official works:**
   - Remove LoRA from your workflow
   - Test modified workflow
   - Compare performance

3. **If official fails:**
   - Update ComfyUI (`git pull`)
   - Clear cache
   - Update NVIDIA drivers
   - Report to TaylorSeer GitHub

4. **If nothing works:**
   - Use your working workflow (125s is already excellent!)
   - TaylorSeer isn't essential for 4-step workflows

---

**The key insight: LoRA + TaylorSeer = CUDA conflict. Remove LoRA or don't use TaylorSeer.**









