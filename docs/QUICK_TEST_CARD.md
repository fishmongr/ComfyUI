# Quick Test - DeleteModelPassthrough

## Status: ✅ READY TO TEST

## Test Command
```powershell
# Kill ComfyUI if running
taskkill /IM python.exe /F

# Start fresh
.\scripts\launch_wan22_rtx5090.bat

# Load: video_wan2_2_14B_i2v_no_sage_test.json
# Run: 81 frames @ 832x1216
```

## Watch For
```
✅ "Using pytorch attention" on startup
✅ "Deleting model from VRAM and RAM..." between passes
❌ NO "offload" messages
✅ Time: 124-137s (vs. previous 146-153s)
```

## Key Changes
- ✅ DeleteModelPassthrough installed (Node 119)
- ✅ SageAttention3 bypassed (using PyTorch SDPA instead)
- ✅ Workflow updated and ready

## Expected Outcome
**HIGH CONFIDENCE** this will eliminate the 845MB offload because:
1. Previous methods only cleared caches (didn't remove models)
2. DeleteModelPassthrough **deletes the 13GB model from memory**
3. Low noise model can load fully (no offload needed)
4. Performance: 124-137s (back to baseline)

## If It Works
Test 161 frames next → Should unlock 10s+ videos! 🚀

## Full Docs
- `docs/READY_TO_TEST.md` - Complete overview
- `docs/DELETE_MODEL_TEST_GUIDE.md` - Detailed test steps
- `docs/SAGEATTENTION3_DISABLED.md` - Why Sage is disabled



