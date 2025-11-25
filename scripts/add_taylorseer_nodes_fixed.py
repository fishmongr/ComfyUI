import json
import uuid

# Load the base workflow
input_path = "user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json"
output_path = "user/default/workflows/video_wan2_2_14B_i2v_TAYLORSEER_FIXED.json"

with open(input_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

print(f"Loaded workflow with {len(workflow['nodes'])} nodes and {len(workflow['links'])} links")

# Workflow uses a dictionary structure for nodes, not an array
# Each node is accessed by its string ID: workflow['nodes']['121']

# Create TaylorSeerLite node for High Noise Model (Node 121)
taylor_high_node = {
    "id": 121,
    "type": "TaylorSeerLite",
    "pos": [744, -360],
    "size": [280, 150],
    "flags": {},
    "order": 25,
    "mode": 0,
    "inputs": [
        {"name": "model", "type": "MODEL", "link": 190}
    ],
    "outputs": [
        {"name": "MODEL", "type": "MODEL", "links": [229], "slot_index": 0}
    ],
    "title": "TaylorSeerLite (High Noise)",
    "properties": {"Node name for S&R": "TaylorSeerLite"},
    "widgets_values": ["wanvideo", 5, 1, 1, 50],
    "color": "#2a363b",
    "bgcolor": "#3f5159"
}

# Create TaylorSeerLite node for Low Noise Model (Node 122)
taylor_low_node = {
    "id": 122,
    "type": "TaylorSeerLite",
    "pos": [744, -230],
    "size": [280, 150],
    "flags": {},
    "order": 26,
    "mode": 0,
    "inputs": [
        {"name": "model", "type": "MODEL", "link": 189}
    ],
    "outputs": [
        {"name": "MODEL", "type": "MODEL", "links": [230], "slot_index": 0}
    ],
    "title": "TaylorSeerLite (Low Noise)",
    "properties": {"Node name for S&R": "TaylorSeerLite"},
    "widgets_values": ["wanvideo", 5, 1, 1, 50],
    "color": "#2a363b",
    "bgcolor": "#3f5159"
}

# Add the new nodes to the dictionary (not array!)
workflow['nodes']['121'] = taylor_high_node
workflow['nodes']['122'] = taylor_low_node

# Add new link 229: TaylorSeer 121 -> ModelSampling 104
workflow['links'].append([229, 121, 0, 104, 0, "MODEL"])

# Add new link 230: TaylorSeer 122 -> ModelSampling 103
workflow['links'].append([230, 122, 0, 103, 0, "MODEL"])

# Update ModelSampling node 104 to receive from TaylorSeer 121 instead of LoRA 101
workflow['nodes']['104']['inputs'][0]['link'] = 229
print("Updated ModelSampling 104 input: link 190 -> 229")
                
# Update ModelSampling node 103 to receive from TaylorSeer 122 instead of LoRA 102
workflow['nodes']['103']['inputs'][0]['link'] = 230
print("Updated ModelSampling 103 input: link 189 -> 230")

# Update LoRA node 101 outputs to include link to TaylorSeer 121
# Current: workflow['nodes']['101']['outputs'][0]['links'] = [190]
# New: workflow['nodes']['101']['outputs'][0]['links'] = [190]  (keep it, TaylorSeer receives it)
print(f"LoRA 101 outputs: {workflow['nodes']['101']['outputs'][0]['links']}")

# Update LoRA node 102 outputs to include link to TaylorSeer 122
# Current: workflow['nodes']['102']['outputs'][0]['links'] = [189]
# New: workflow['nodes']['102']['outputs'][0]['links'] = [189]  (keep it, TaylorSeer receives it)
print(f"LoRA 102 outputs: {workflow['nodes']['102']['outputs'][0]['links']}")

# Update metadata
workflow['last_node_id'] = 122
workflow['last_link_id'] = 230
workflow['id'] = str(uuid.uuid4())

# Save the new workflow
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Created: {output_path}")
print(f"Added nodes: 121 (TaylorSeerLite High Noise), 122 (TaylorSeerLite Low Noise)")
print(f"New workflow has {len(workflow['nodes'])} nodes and {len(workflow['links'])} links")
print("\nNew flow:")
print("  High Noise: UNET 95 -> LoRA 101 -> [Link 190] -> TaylorSeer 121 -> [Link 229] -> ModelSampling 104")
print("  Low Noise:  UNET 96 -> LoRA 102 -> [Link 189] -> TaylorSeer 122 -> [Link 230] -> ModelSampling 103")

