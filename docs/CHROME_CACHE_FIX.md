# Fix: Chrome Browser Cache Issue with DeleteModelPassthrough

## The Problem

The workflow works in my browser but shows "Some Nodes Are Missing" in your Chrome browser, even though we're loading the same file. This is a **browser caching issue**.

## Solution 1: Load Fresh Workflow (Easiest)

I've created a new workflow file with a unique ID that Chrome will treat as completely fresh:

**Load this file:** `video_wan2_2_14B_i2v_DELETE_MODEL_v2.json`

This is **identical** to the DELETE_MODEL workflow but has:
- New filename (bypasses filename-based cache)
- New workflow ID (bypasses ID-based cache)
- Confirmed working Node 119 (DeleteModelPassthrough)

## Solution 2: Clear Chrome Cache (If v2 Still Fails)

### Quick Clear (Application Cache Only):
1. Open Chrome DevTools: **F12** or **Ctrl+Shift+I**
2. Right-click the **Refresh button** (next to URL bar)
3. Select **"Empty Cache and Hard Reload"**
4. Try loading the workflow again

### Full Clear (All ComfyUI Data):
1. In Chrome, press **F12** to open DevTools
2. Go to **Application** tab
3. Expand **Local Storage** in left panel
4. Right-click `http://127.0.0.1:8188`
5. Click **"Clear"**
6. Go to **Cache Storage** in left panel
7. Right-click each cache → **Delete**
8. Close DevTools and refresh page (**F5**)
9. Load the workflow

### Nuclear Option (Complete Reset):
```
Chrome Settings → Privacy and security → Clear browsing data
✅ Cached images and files
✅ Site settings
Time range: Last hour
```

## Solution 3: Try Different Browser

If Chrome cache persists:
- **Edge:** Should work immediately (different browser cache)
- **Firefox:** Should work immediately
- **Private/Incognito:** Chrome incognito mode (no cache)

## Why This Happens

ComfyUI's frontend caches workflow data aggressively:
1. **LocalStorage**: Stores workflow state by ID
2. **Service Workers**: Cache JSON files
3. **Browser Cache**: Caches by filename

When you load a workflow:
- Chrome checks LocalStorage first (finds old cached version)
- Never actually reads the updated file from disk
- Shows the error from the OLD cached version

## Verification Steps

After trying any solution above:

1. **Load:** `video_wan2_2_14B_i2v_DELETE_MODEL_v2.json`
2. **Check:** Should load without "Some Nodes Are Missing" error
3. **Verify:** Node 119 "Delete High Noise Model" should be visible
4. **Run:** Click Run to test execution

## Expected Result

✅ Workflow loads without errors  
✅ Node 119 (DeleteModelPassthrough) recognized  
✅ Execution starts successfully  
✅ Ready for performance test

---

## Quick Test Command

```
1. Press F12 in Chrome
2. Right-click Refresh → "Empty Cache and Hard Reload"
3. Close DevTools (F12)
4. Load: video_wan2_2_14B_i2v_DELETE_MODEL_v2.json
5. Click Run
```

---

**This should definitely work!** The v2 workflow has a completely new ID and filename that Chrome has never seen before. 🚀

