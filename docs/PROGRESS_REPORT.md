# Wan 2.2 i2v Optimization - Progress Report

## ✅ Completed Tasks

### 1. System Audit (COMPLETED)
- ✅ Documented full system configuration
- ✅ GPU: RTX 5090, 32GB VRAM, Driver 580.97
- ✅ PyTorch: 2.10.0.dev20251121+cu128 with CUDA 12.8
- ✅ Environment snapshot tool created: `scripts/save_env.py`
- ✅ Identified key issue: `TORCH_COMPILE=0` (disabled)
- ✅ High Performance power plan confirmed
- ✅ Full audit saved to: `docs/SYSTEM_AUDIT.md` and `docs/env_snapshot_rtx5090.json`

### 2. Optimized Launch Scripts (COMPLETED)
- ✅ RTX 5090 script: `scripts/launch_wan22_rtx5090.bat`
  - --disable-pinned-memory (required for RTX 50 series)
  - --highvram (32GB allows keeping everything in VRAM)
  - --use-sage-attention (optimal for Blackwell/Ada)
  - --force-channels-last (memory layout optimization)
  - Environment variables: TORCH_COMPILE=1, optimized CUDA allocator

- ✅ RTX 4090 script: `scripts/launch_wan22_rtx4090.bat`
  - --normalvram with --reserve-vram 4 (24GB needs careful management)
  - SageAttention3 (still optimal for Ada)
  - Conservative memory settings for two-pass workflow

- ✅ A100 script: `scripts/launch_wan22_a100.bat`
  - --gpu-only (40/80GB is plenty)
  - --use-flash-attention (optimal for Ampere, NOT SageAttention3)
  - Data center optimizations

## 🚧 In Progress

### 3. Automated Benchmark Framework
Status: Framework structure created, needs ComfyUI workflow integration

**Created Files:**
- `scripts/wan22_benchmark.py` - Main benchmark runner with:
  - GPU monitoring (VRAM, timing)
  - OOM error handling
  - Two-pass workflow structure
  - Result logging and summary reports
  - Performance regression detection (alerts if > 85s per pass)

**What's Needed Next:**
The benchmark framework is ready but needs actual ComfyUI workflow execution integrated. Currently has placeholder simulation functions that need to be replaced with real workflow calls.

## 📋 Next Steps (Ready for Execution)

### Immediate: Before Running Baseline Tests

**CRITICAL DECISION NEEDED:** Two-pass workflow implementation approach

There are two ways to integrate Wan 2.2 i2v two-pass workflow:

**Option A: Native ComfyUI Nodes (RECOMMENDED)**
- Use `comfy_extras/nodes_wan.py` which has `Wan22FunControlToVideo` node
- Build workflows in ComfyUI UI, export to JSON
- Benchmark framework loads and executes workflows
- **Pros:** Visual workflow building, easier to modify, standard approach
- **Cons:** Need to build workflows first

**Option B: Direct API Integration**
- Call ComfyUI's Python API directly from benchmark script
- Programmatically construct workflow
- **Pros:** Fully automated, no manual workflow building
- **Cons:** More complex, harder to debug, less flexible

**RECOMMENDATION:** Use Option A - build workflows in ComfyUI UI first, then automate

### Step-by-Step Plan to Continue:

1. **User Action Required: Start ComfyUI**
   ```
   cd C:\Users\markl\Documents\git\ComfyUI
   .\scripts\launch_wan22_rtx5090.bat
   ```
   
2. **User Action: Build Test Workflow in UI**
   - Load Wan2.2 i2v high_noise model
   - Load 4-step LoRA (high_noise)
   - Connect to Wan22FunControlToVideo node
   - Set resolution: 832x1216, frames: 81 (5s)
   - Generate first pass
   - Load low_noise model + LoRA
   - Generate second pass (refinement)
   - Save workflow as: `workflows/wan22_i2v_baseline_5s.json`

3. **Integrate Workflow into Benchmark**
   - Modify `wan22_benchmark.py` to load and execute saved workflow
   - Replace `_simulate_generation()` with real workflow execution

4. **Run Baseline Tests**
   - Execute: `python scripts/wan22_benchmark.py`
   - Test both pass orders (high→low, low→high)
   - Test 5s and 10s durations
   - Verify 67-80s per-pass target is met

5. **Install Frame Interpolation**
   - Research best ComfyUI node for RIFE/FILM
   - Install via ComfyUI-Manager
   - Download model weights

6. **Continue with optimization testing...**

## 🔍 Key Findings So Far

### Environment Issues Identified:
1. **TORCH_COMPILE=0**: Was disabled, launch scripts now enable it
2. **No CUDA allocator config**: Now set in launch scripts
3. **Optimal attention unclear**: Need to test SageAttention3 vs FlashAttention

### Performance Targets:
- **Per pass**: 67-80s for 5s video (81 frames) @ 832x1216
- **Two-pass total**: 134-160s
- **With interpolation**: < 180s for 5s@32fps final output

### Hardware Configuration:
- Excellent: RTX 5090 with 32GB VRAM
- CUDA 12.8 + PyTorch 2.10 properly configured
- High Performance power plan active
- All models and LoRAs present

## 📝 User Input Needed

**To proceed with baseline testing, please:**

1. Confirm you want to use Option A (build workflows in UI first)
2. OR provide existing workflow JSON files if you have them
3. OR let me know if you prefer Option B (direct API integration)

**Once workflows are ready, the automation can handle:**
- All benchmark testing
- Frame interpolation comparison
- Optimization matrix testing
- Report generation

## 📂 Files Created

```
ComfyUI/
├── docs/
│   ├── SYSTEM_AUDIT.md                    # Full system audit
│   └── env_snapshot_rtx5090.json         # Environment snapshot
├── scripts/
│   ├── save_env.py                       # Environment snapshot tool
│   ├── launch_wan22_rtx5090.bat          # RTX 5090 optimized launch
│   ├── launch_wan22_rtx4090.bat          # RTX 4090 optimized launch
│   ├── launch_wan22_a100.bat             # A100 optimized launch
│   └── wan22_benchmark.py                # Benchmark framework (needs workflow integration)
└── workflows/
    └── (empty - need to create test workflows)
```

## 🎯 Success Criteria

- [x] System fully audited and documented
- [x] Optimized launch scripts for all GPU tiers
- [ ] Baseline performance verified (67-80s per pass)
- [ ] Frame interpolation working (RIFE/FILM comparison)
- [ ] Optimization matrix tested
- [ ] Docker containers configured
- [ ] Final report delivered

**Current Status:** Ready for workflow creation and baseline testing

