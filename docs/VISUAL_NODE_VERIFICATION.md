# How to Verify DeleteModelPassthrough Node in ComfyUI UI

## Visual Identification (No Node Numbers Needed)

### What to Look For:

**Node Title:** `"Delete High Noise Model"`

**Node Type:** Should show as `"Delete Model (Passthrough Any)"` when you hover or click it

**Location:** Between the two KSampler nodes (High Noise Pass → DeleteModel → Low Noise Pass)

**Node Color:** Should have a reddish/pink background (color: #A88, bgcolor: #C99)

---

## Visual Verification Steps

### 1. Check the Node Exists

**Look for a node titled:**
```
Delete High Noise Model
```

**It should be positioned:**
- **AFTER** the first KSampler (High Noise Pass, does steps 0-2)
- **BEFORE** the second KSampler (Low Noise Pass, does steps 2-4)

### 2. Check It's Connected

The node should have **TWO inputs** (left side):
1. **Top input:** Connected from the first KSampler's LATENT output
2. **Bottom input:** Connected from the model path (LoRA/ModelSampling nodes)

The node should have **ONE output** (right side):
- Connected TO the second KSampler's `latent_image` input

### 3. Visual Diagram

```
[KSampler: High Noise Pass]
    │ (LATENT output)
    ↓
[Delete High Noise Model]  ← THIS NODE
    │ (passes LATENT through)
    ↓
[KSampler: Low Noise Pass]
```

---

## How to Enable Node ID Display (Optional)

If you want to see node IDs like I reference:

### Method 1: Node Properties
1. **Right-click** any node
2. Select **"Properties"** or **"Node Properties"**
3. Look for **"id"** field

### Method 2: Browser Console
1. Press **F12** (open DevTools)
2. Go to **Console** tab
3. Type: `app.graph._nodes.map(n => ({id: n.id, title: n.title, type: n.type}))`
4. Press Enter
5. Look for the node with `title: "Delete High Noise Model"`

---

## Quick Visual Test

### ✅ CORRECT (Node is connected):
```
[First KSampler] ──LATENT──> [Delete High Noise Model] ──LATENT──> [Second KSampler]
```

### ❌ WRONG (Node is bypassed or disconnected):
```
[First KSampler] ──LATENT──────────────────────────────> [Second KSampler]
                              (skips Delete node)
```

---

## What You Should See When It Works

### Before First Pass:
- Normal workflow execution starts

### After First Pass (Between the two KSamplers):
**Console output:**
```
📋 Models in loaded_models():
   0: ModelPatcher (~13GB)
   1: ModelPatcher (~13GB)
Managed models: 2 → 1
GPU allocated freed: ~13.000 GB
SUCCESS: Model removed from management system!
```

### During Second Pass:
- NO "offloaded" messages
- Smooth execution

---

## Alternative: Search Node by Name

In ComfyUI:
1. Press **Ctrl+F** or click the **search icon**
2. Type: `Delete High Noise Model`
3. It should highlight the node

---

## Screenshot Reference (What to Look For)

The node should look like this in the UI:

```
┌─────────────────────────────┐
│ Delete High Noise Model     │  ← Title
│ (Delete Model Passthrough)  │  ← Type
├─────────────────────────────┤
│ ◄ data (from KSampler)      │  ← Input 1
│ ◄ model (from Sage3/Lora)   │  ← Input 2
│ ► output (to KSampler) ────►│  ← Output (MUST be connected!)
└─────────────────────────────┘
```

**Key:** The **output arrow** on the right MUST have a line going to the second KSampler!

---

## Quick Verification Without Node IDs

Just answer these questions:

1. ✅ Do you see a node titled **"Delete High Noise Model"**?
2. ✅ Is it **between** the two KSampler nodes?
3. ✅ Does it have a **wire coming OUT of it** (right side) going to the second KSampler?

If all 3 are YES → The node is properly connected!

If #3 is NO → The node is disconnected and won't execute!

---

**You don't need to see node numbers - just verify the "Delete High Noise Model" node exists and has a wire coming out of it to the next KSampler!** 🚀

