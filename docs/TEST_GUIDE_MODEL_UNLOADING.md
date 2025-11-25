# 🧪 TEST GUIDE - Model Unloading Fix

## ✅ What Was Done

Added TWO nodes between your high_noise and low_noise passes:
1. **`easy cleanGpuUsed`** (Node 118) - Unloads models from VRAM
2. **`easy clearCacheAll`** (Node 119) - Clears ComfyUI caches

**Position**: Between KSampler 86 (High Noise) → KSampler 85 (Low Noise)

---

## 🚀 How To Test

### **Step 1: Restart ComfyUI**

**Important**: The new custom nodes require a restart!

```powershell
# If ComfyUI is running, stop it (Ctrl+C)
# Then restart:
.\scripts\launch_wan22_rtx5090.bat
```

### **Step 2: Open Updated Workflow**

In ComfyUI:
1. Load workflow: `user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json`
2. You should see TWO new RED nodes between the two KSamplers:
   - 🔥 "Unload High Noise Model"
   - 🧹 "Clear Cache"

### **Step 3: Test 81 Frames**

**Settings to use:**
- Image: Your polar bear image
- Resolution: 832x1216
- **Frames: 73** (81 total with start frame)
- Steps: 4 (2 high noise, 2 low noise)

**Expected behavior:**
- **Before fix**: Offloading starts, 146-160s
- **After fix**: NO offloading, ~120s! 🎯

### **Step 4: Watch Console Output**

**What to look for:**

**✅ GOOD (No offloading):**
```
loaded completely
loaded completely; 14971.79 MB usable, 13629.08 MB loaded, full load: True
```

**❌ BAD (Offloading - if this still happens):**
```
loaded partially; 11332.26 MB usable, 11332.26 MB loaded, 2296.82 MB offloaded
```

---

## 📊 Benchmarks To Track

Record these times:

### **Test 1: 73 Frames (4.6s)**
- Generation time: _______s
- Offloading? YES / NO

### **Test 2: 81 Frames (5.0s)**  
- Generation time: _______s
- Offloading? YES / NO

### **Test 3: 161 Frames (10.0s)**
- Generation time: _______s
- Offloading? YES / NO

---

## 🎯 Success Criteria

**Fix is working if:**
1. ✅ 81 frames completes in **~120s** (vs 146-160s before)
2. ✅ Console shows "**loaded completely**" for both models
3. ✅ NO "**loaded partially**" or "**offloaded**" messages
4. ✅ 161 frames WORKS (didn't before!)

---

## ⚠️ If Nodes Are Missing

If you see errors about "easy cleanGpuUsed" or "easy clearCacheAll" not found:

1. Check custom nodes installed:
   ```powershell
   dir custom_nodes\ComfyUI-Easy-Use
   ```

2. If missing, install:
   ```powershell
   cd custom_nodes
   git clone https://github.com/yolain/ComfyUI-Easy-Use
   cd ..
   ```

3. Restart ComfyUI

---

## 🔍 Troubleshooting

### **Problem: Still offloading at 81 frames**

**Solution A**: Increase `--reserve-vram` in launch script:
```batch
--reserve-vram 6  (instead of 4)
```

**Solution B**: Try `--normalvram` instead of `--highvram`:
```batch
--normalvram ^
--reserve-vram 6 ^
```

### **Problem: Nodes show "Cannot find node"**

**Solution**: ComfyUI-Easy-Use not installed. See "If Nodes Are Missing" above.

### **Problem: Generation fails completely**

**Solution**: The nodes might be interfering. Bypass them:
1. Right-click each red node
2. Select "Bypass"
3. This will skip them but keep connections intact

---

## 📈 Expected Results After Fix

| Frames | Before Fix     | After Fix      | Improvement |
|--------|----------------|----------------|-------------|
| 61     | ~93s (no off)  | ~93s (no off)  | Same        |
| 81     | **146-160s** ❌ | **~120s** ✅    | **20-25%**  |
| 161    | OOM/Very slow  | **~200-220s** ✅| Possible!   |

---

## 🎬 Next Optimizations (After This Works)

Once model unloading is confirmed working:

1. **Block Swap**: Add `WanVideoBlockSwap` node with 25 blocks
2. **LoRA Tuning**: High noise = 3.0, Low noise = 1.0
3. **Frame Interpolation**: Add RIFE for 16fps → 32fps

---

## 📝 Report Back

Please let me know:
1. Did ComfyUI restart successfully?
2. Do you see the two RED nodes in the workflow?
3. What generation time did you get for 81 frames?
4. Did console show "loaded completely" or "loaded partially"?

**Good luck with the test!** 🚀

