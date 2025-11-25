# SageAttention3 Note

## Issue Found

The `--use-sage-attention` ComfyUI launch flag requires the `sageattention` pip package, which has installation issues on Windows with the current setup.

## Solution

Your workflow already uses **ComfyUI-SageAttention3 custom node** with the `Sage3AttentionOnlySwitch` nodes (nodes 117 and 118 in your workflow). This is actually better because:

1. **Per-workflow control**: You can enable/disable SageAttention3 per workflow
2. **No launch flag needed**: The custom node handles it
3. **Already working**: Your workflow has it configured with `enable=true`

## Your Workflow Configuration

Your workflow already has SageAttention3 properly configured:
- Node 117: `Sage3AttentionOnlySwitch` for Pass 1 (high noise)
- Node 118: `Sage3AttentionOnlySwitch` for Pass 2 (low noise)
- Both set to `enable=true`

## Updated Launch Script

I've updated `scripts/launch_wan22_rtx5090.bat` to:
- Remove `--use-sage-attention` flag
- Keep all other optimizations (TORCH_COMPILE=1, highvram, etc.)
- Rely on the custom node for SageAttention3

## Action Required

**Restart ComfyUI with the updated launch script:**

```batch
cd C:\Users\markl\Documents\git\ComfyUI
.\scripts\launch_wan22_rtx5090.bat
```

This should start without any prompts. Your workflow will still use SageAttention3 via the custom node.

## Performance Testing

Once ComfyUI starts:
1. Load your workflow (`video_wan2_2_14B_i2v (2).json`)
2. Run a test generation
3. Time both passes
4. **Target**: 67-80s per pass

If you get this performance, the environment optimizations are working!

## Alternative: Test Without SageAttention3

If you want to test performance without SageAttention3:
1. Open your workflow
2. Set `enable=false` on nodes 117 and 118
3. Run test generation
4. Compare timing

This will show the impact of SageAttention3 optimization.

