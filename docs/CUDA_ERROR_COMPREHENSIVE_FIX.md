# CUDA "Invalid Argument" Error - Comprehensive Fix (UPDATED)

## **Error Still Occurring After Initial Fix**

If you're still getting the error after restarting, it means the synchronization needs to be more aggressive.

---

## **Enhanced Fixes Applied**

### **comfy/model_patcher.py - 3 Locations**

**1. At the start of `detach()` function (line ~960)**
```python
def detach(self, unpatch_all=True):
    # Synchronize CUDA before detaching to ensure all operations are complete
    import torch
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    # ... rest of function
```

**2. Before model unloading in `unpatch_model()` (line ~836)**
```python
# Synchronize ALL CUDA devices before moving model
import torch
if torch.cuda.is_available():
    torch.cuda.synchronize()
self.model.to(device_to)
```

**3. Before model loading in `load()` (line ~760)**
```python
# Synchronize ALL CUDA devices before loading modules
import torch
if torch.cuda.is_available():
    torch.cuda.synchronize()
for x in load_completely:
    x[2].to(device_to)
```

### **TaylorSeer nodes.py - 10 Locations**

Added `torch.cuda.synchronize()` after every async block swap operation in:
- `flux_block_swap()`
- `hidream_block_swap()`
- `wanvideo_block_swap()`
- `qwenimage_block_swap()`
- All cleanup operations in `TaylorSeer` and `TaylorSeerLite`

---

## **What Changed in This Update**

### **Problem with Previous Fix:**
- Only synchronized specific CUDA device
- Checked `self.model.device.type == 'cuda'` which might be False/None at unload time

### **Solution:**
- Now synchronizes **ALL CUDA devices** with `torch.cuda.synchronize()` (no device parameter)
- Checks `torch.cuda.is_available()` instead of specific device
- Added sync at the **start** of `detach()` function (catches issues earlier)

---

## **What You Need to Do**

### **1. Restart ComfyUI (Required)**

```powershell
taskkill /IM python.exe /F
.\scripts\launch_wan22_rtx5090.bat
```

### **2. Test Workflow Again**

Load and run: `video_wan2_2_14B_i2v_TAYLORSEER.json`

**Expected:**
- ✅ No "CUDA error: invalid argument"
- ✅ First pass completes
- ✅ Second model loads successfully
- ✅ Second pass completes
- ✅ ~40-50 seconds for 81 frames

---

## **If It STILL Fails**

###Option 1: Use CUDA_LAUNCH_BLOCKING for Diagnosis

```powershell
$env:CUDA_LAUNCH_BLOCKING="1"
python main.py
```

This will:
- Make all CUDA operations synchronous
- Give you the **exact** error location
- Help identify if it's a different issue

Run your workflow and share the error log.

### **Option 2: Test Without TaylorSeer**

1. Open your workflow
2. Remove/bypass the TaylorSeerLite nodes
3. Reconnect: `LoRA → ModelSampling` (direct connection)
4. Save as: `video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json`
5. Test this version

**If this works:** The issue is specifically TaylorSeer  
**If this also fails:** The issue is broader (possibly CUDA driver/hardware)

### **Option 3: Check CUDA/PyTorch Installation**

```powershell
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

Expected output:
```
True
12.1  # (or your CUDA version)
```

If you see `False`, CUDA is not properly configured.

---

## **Why This Might Still Fail**

### **Possible Reasons:**

1. **CUDA Driver Issue**
   - Corrupted CUDA state
   - Driver needs restart
   - **Solution:** Restart your computer

2. **Memory Corruption**
   - VRAM is fragmented/corrupted
   - Previous crash left CUDA in bad state
   - **Solution:** Full system restart

3. **Hardware Issue**
   - GPU overheating
   - Memory errors on GPU
   - **Solution:** Check `nvidia-smi` for GPU health

4. **TaylorSeer Itself Has Bugs**
   - The custom node might have issues beyond async ops
   - **Solution:** Disable TaylorSeer completely

---

## **Diagnostic Steps**

### **1. Check GPU Health**

```powershell
nvidia-smi
```

Look for:
- **Temperature:** Should be < 85°C
- **Power:** Should be within normal range
- **Memory errors:** Should be 0
- **Compute processes:** Should show Python when ComfyUI is running

### **2. Check CUDA Version Compatibility**

```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.version.cuda}')"
```

Ensure PyTorch CUDA version matches your driver's CUDA version (or is compatible).

### **3. Clear CUDA Cache Manually**

Add this to your workflow (temporary debugging):

Create a custom node or add to ComfyUI startup:
```python
import torch
import gc
torch.cuda.empty_cache()
gc.collect()
```

---

## **Nuclear Option: Full Reset**

If nothing works:

### **1. Stop ComfyUI**
```powershell
taskkill /IM python.exe /F
```

### **2. Clear GPU Memory**
```powershell
nvidia-smi --gpu-reset
```

### **3. Restart Computer**
(This clears ALL CUDA state)

### **4. Start Fresh**
```powershell
.\scripts\launch_wan22_rtx5090.bat
```

### **5. Test Simple Workflow First**
- Test a simple workflow (not TaylorSeer)
- If that works, gradually add complexity

---

## **Alternative: Disable TaylorSeer Temporarily**

Until we resolve this, you can:

1. **Use your working workflow** without TaylorSeer
   - `video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json`
   - Performance: ~125s for 81 frames (still fast!)

2. **Wait for TaylorSeer update**
   - The TaylorSeer developers may release a fix
   - Check: https://github.com/mav-rik/ComfyUI-TaylorSeer

3. **Report to TaylorSeer developers**
   - Share your error logs
   - They might have additional solutions

---

## **Summary of All Changes**

| File | Location | What Changed |
|------|----------|--------------|
| `comfy/model_patcher.py` | Line ~960 (detach) | Added sync at function start |
| `comfy/model_patcher.py` | Line ~841 (unpatch_model) | Strengthened sync (all devices) |
| `comfy/model_patcher.py` | Line ~765 (load) | Strengthened sync (all devices) |
| `custom_nodes/ComfyUI-TaylorSeer/nodes.py` | All block swaps | Added sync after async transfers |

---

**Please restart ComfyUI with these enhanced fixes and test again. If it still fails, we'll need to investigate deeper or disable TaylorSeer temporarily.**









