# How to Disable TaylorSeer and Use Working Workflow

## **Quick Solution: Use Non-TaylorSeer Workflow**

If the CUDA error persists, the fastest solution is to use your working baseline workflow.

---

## **Option 1: Load Your Working Workflow (Fastest)**

Simply load: **`video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json`**

This is your workflow that was working **before** you added TaylorSeer.

**Expected Performance:**
- ✅ No crashes
- ✅ ~125-137 seconds for 81 frames
- ✅ Reliable and tested

---

## **Option 2: Remove TaylorSeer from Current Workflow**

If you want to keep other settings from your TaylorSeer workflow:

### **Steps:**

1. **Open the workflow in ComfyUI:**
   - Load: `video_wan2_2_14B_i2v_TAYLORSEER.json`

2. **Find the TaylorSeerLite nodes:**
   - Should be between LoRA and ModelSampling nodes
   - Likely named "TaylorSeer High Noise" and "TaylorSeer Low Noise"
   - Node IDs: 119, 120, 121, or 122 (depends on your workflow)

3. **Delete TaylorSeerLite nodes:**
   - Click on each TaylorSeerLite node
   - Press `Delete` or right-click → Delete

4. **Reconnect the links:**
   - **High Noise Path:**
     - Connect: `LoRA 101` → `ModelSampling 104`
   - **Low Noise Path:**
     - Connect: `LoRA 102` → `ModelSampling 103`

5. **Save with NEW filename:**
   ```
   video_wan2_2_14B_i2v_NO_TAYLORSEER_CLEANED.json
   ```
   - **Important:** Use a NEW filename to avoid browser cache issues!

6. **Test the workflow**

---

## **Option 3: Temporarily Disable TaylorSeer Custom Node**

If you want to fully disable TaylorSeer from ComfyUI:

### **Method 1: Rename the folder**

```powershell
cd custom_nodes
Rename-Item "ComfyUI-TaylorSeer" "ComfyUI-TaylorSeer.disabled"
```

Then restart ComfyUI.

### **Method 2: Delete the folder**

```powershell
Remove-Item -Recurse -Force custom_nodes\ComfyUI-TaylorSeer
```

Then restart ComfyUI.

**Note:** You can always reinstall TaylorSeer later if a fix becomes available.

---

## **Option 4: Try Different TaylorSeer Settings**

If you really want TaylorSeer to work, try these settings:

### **Lower Settings (Less Aggressive):**

On your TaylorSeerLite nodes, try:
- `fresh_threshold`: 7 (instead of 5)
- `max_order`: 0 (instead of 1)
- `first_enhance`: 5 (instead of 1)
- `last_enhance`: 40 (instead of 50)

These are less aggressive and might avoid the CUDA issue.

---

## **Diagnostic: Check if Fixes Were Loaded**

To verify the code fixes actually loaded:

### **1. Restart ComfyUI (if you haven't)**

```powershell
taskkill /IM python.exe /F
.\scripts\launch_wan22_rtx5090.bat
```

### **2. Run TaylorSeer workflow**

### **3. Look for debug messages in console:**

You should see:
```
[DEBUG] Synchronizing CUDA before detach
[DEBUG] Synchronizing CUDA before unpatch to cpu
```

**If you DON'T see these messages:**
- The code changes weren't loaded
- ComfyUI is using cached Python bytecode
- You might need to delete `__pycache__` folders

**If you DO see these messages but still get errors:**
- The synchronization isn't enough
- TaylorSeer has deeper issues
- **Recommendation:** Disable TaylorSeer

---

## **Clear __pycache__ (If Code Changes Not Loading)**

```powershell
# Stop ComfyUI first
taskkill /IM python.exe /F

# Clear cache
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force

# Restart
.\scripts\launch_wan22_rtx5090.bat
```

---

## **Recommended Approach**

**For reliable video generation right now:**

1. ✅ Use: `video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json`
2. ✅ Performance: ~125s for 81 frames (still excellent!)
3. ✅ No crashes, tested and working

**For experimenting with TaylorSeer:**

1. ⚠️ Try the diagnostic steps above
2. ⚠️ If errors persist, wait for TaylorSeer update
3. ⚠️ Or report issue to TaylorSeer developers: https://github.com/mav-rik/ComfyUI-TaylorSeer/issues

---

## **Performance Comparison**

| Workflow | Time (81 frames) | Status |
|----------|------------------|--------|
| **Without TaylorSeer** | ~125-137s | ✅ **Working reliably** |
| **With TaylorSeer (if it worked)** | ~40-50s | ❌ Crashing with CUDA error |

**Conclusion:** The working workflow is already fast. TaylorSeer's 3x speedup is nice but not essential.

---

## **Next Steps**

1. **Use working workflow** (`video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json`)
2. **Get your videos generated reliably**
3. **Check back later** for TaylorSeer updates/fixes
4. **Focus on quality and results** rather than chasing the speedup

---

**Bottom line: You have a working, fast solution. Use it and move forward with your project!**









