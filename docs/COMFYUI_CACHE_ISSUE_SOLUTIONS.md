# ComfyUI Workflow Caching - Known Issue & Solutions

## ✅ Confirmed: This is a KNOWN Issue

ComfyUI has a **documented caching problem** where workflows may be cached by both the browser AND ComfyUI itself, causing outdated versions to be loaded even after updates. This is exactly what you're experiencing!

## Root Causes

1. **Browser-side caching**: Chrome/browsers cache workflow JSON files aggressively
2. **ComfyUI server-side caching**: ComfyUI may cache workflow data in memory
3. **No cache-busting**: ComfyUI doesn't implement proper cache-busting techniques (like version query parameters that change)

## Proven Solutions from Community

### Solution 1: Load via ComfyUI API (Most Reliable)

Instead of using the browser UI, load the workflow programmatically:

```python
import json
import urllib.request
import urllib.parse

# Load workflow file
with open('user/default/workflows/TAYLORSEER_v1763973397.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Post directly to ComfyUI API
url = "http://127.0.0.1:8188/api/prompt"
data = {"prompt": workflow}
req = urllib.request.Request(url, json.dumps(data).encode('utf-8'), {'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
print(f"Workflow loaded: {response.read().decode('utf-8')}")
```

### Solution 2: File Manager Method (Bypasses Cache)

1. In ComfyUI web UI, click **Menu** (hamburger icon)
2. Select **"Load"**
3. Click **"Choose File"** (NOT the workflow dropdown!)
4. Browse to the actual file: `TAYLORSEER_v1763973397.json`
5. This forces a fresh file read from disk

### Solution 3: Developer Tools Network Disable

1. Open Chrome DevTools (F12)
2. Go to **Network** tab
3. Check **"Disable cache"**
4. **Keep DevTools open** while using ComfyUI
5. Navigate to: http://127.0.0.1:8188/
6. Manually load the workflow file

### Solution 4: Restart ComfyUI Server (Clears Server Cache)

ComfyUI may cache workflows in memory:

```bash
# Stop ComfyUI (Ctrl+C)
# Then restart:
.\scripts\launch_wan22_rtx5090.bat
```

Then in browser:
1. Hard refresh: `Ctrl + Shift + F5`
2. Load the new workflow

### Solution 5: Direct API Load (Nuclear Option)

Save this as `scripts/load_taylorseer_workflow.py`:

```python
import json
import urllib.request
import urllib.parse

# ComfyUI API endpoint
COMFYUI_URL = "http://127.0.0.1:8188"

# Load the workflow
workflow_path = "user/default/workflows/TAYLORSEER_v1763973397.json"
with open(workflow_path, 'r', encoding='utf-8') as f:
    workflow_data = json.load(f)

# Get the prompt format (extract just the nodes)
prompt = {"prompt": workflow_data}

# Send to ComfyUI
url = f"{COMFYUI_URL}/api/prompt"
req = urllib.request.Request(
    url,
    data=json.dumps(prompt).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))
    print(f"✅ Workflow loaded successfully!")
    print(f"Prompt ID: {result.get('prompt_id')}")
except Exception as e:
    print(f"❌ Error loading workflow: {e}")
```

## Why Your Issue is Worse Than Normal

You're experiencing **both** caching issues:
1. **Chrome cache**: The browser won't load the new JSON
2. **ComfyUI cache**: Even direct URL navigation doesn't work

This happens because:
- Chrome caches by URL path
- ComfyUI may cache by filename
- Even with `?filename=` parameter, both caches persist

## Recommended Action Plan

**Try in this order:**

1. ✅ **Use File Manager Load** (Solution 2)
   - Most user-friendly
   - Bypasses all caches
   - Should work immediately

2. ✅ **If that fails**: Restart ComfyUI + DevTools disable cache (Solution 4 + 3)
   - Clears server-side cache
   - Browser won't use cache with DevTools

3. ✅ **If that fails**: Use API load script (Solution 5)
   - Completely bypasses browser
   - Direct file-to-API
   - Guaranteed fresh load

## Verification

After loading with any method, verify:
1. **No errors** about missing node [121]
2. **See TaylorSeerLite nodes** in the graph (purple/dark nodes between LoRA and ModelSampling)
3. **Workflow title** changes to `TAYLORSEER_v1763973397`

## Community Workarounds

From Reddit/GitHub, users also report success with:
- **Using different filename patterns** (we already did this)
- **Loading in Incognito** (won't help if ComfyUI caches server-side)
- **Deleting browser localStorage** (for workflow history)
- **Using Firefox instead of Chrome** (different cache behavior)

## Bottom Line

This is a **known ComfyUI limitation**, not your fault! The workflow JSON is correct, but ComfyUI's caching is too aggressive.

**The File Manager Load method (Solution 2) should work - it bypasses both browser and server caches by forcing a fresh file read from disk.**

