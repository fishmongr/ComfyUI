import json
import uuid
import time

# Load the base workflow
input_path = "user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json"
# Create unique filename with timestamp
timestamp = int(time.time())
output_path = f"user/default/workflows/TAYLORSEER_v{timestamp}.json"

with open(input_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

print(f"Loaded workflow with {len(workflow['nodes'])} nodes and {len(workflow['links'])} links")

# Find nodes 101, 102, 103, 104 in the array
node_101_idx = next(i for i, n in enumerate(workflow['nodes']) if n['id'] == 101)
node_102_idx = next(i for i, n in enumerate(workflow['nodes']) if n['id'] == 102)
node_103_idx = next(i for i, n in enumerate(workflow['nodes']) if n['id'] == 103)
node_104_idx = next(i for i, n in enumerate(workflow['nodes']) if n['id'] == 104)

print(f"Found: Node 101 at index {node_101_idx}, Node 102 at index {node_102_idx}")
print(f"Found: Node 103 at index {node_103_idx}, Node 104 at index {node_104_idx}")

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

# Add the new nodes to the array
workflow['nodes'].append(taylor_high_node)
workflow['nodes'].append(taylor_low_node)

# Add new links: TaylorSeer -> ModelSampling
workflow['links'].append([229, 121, 0, 104, 0, "MODEL"])
workflow['links'].append([230, 122, 0, 103, 0, "MODEL"])

# Update ModelSampling nodes to receive from TaylorSeer instead of LoRA
workflow['nodes'][node_104_idx]['inputs'][0]['link'] = 229
workflow['nodes'][node_103_idx]['inputs'][0]['link'] = 230

print("Updated ModelSampling 104 input: link 190 -> 229")
print("Updated ModelSampling 103 input: link 189 -> 230")

# LoRA outputs stay the same (190 and 189), they now go to TaylorSeer
print(f"LoRA 101 outputs: {workflow['nodes'][node_101_idx]['outputs'][0]['links']}")
print(f"LoRA 102 outputs: {workflow['nodes'][node_102_idx]['outputs'][0]['links']}")

# Update metadata with UNIQUE ID to force cache bypass
workflow['last_node_id'] = 122
workflow['last_link_id'] = 230
workflow['id'] = str(uuid.uuid4())
workflow['version'] = timestamp / 1000.0  # Unique version number

# Save the new workflow
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Created: {output_path}")
print(f"Workflow ID: {workflow['id']}")
print(f"Workflow Version: {workflow['version']}")
print(f"Added nodes: 121 (TaylorSeerLite High Noise), 122 (TaylorSeerLite Low Noise)")
print(f"New workflow has {len(workflow['nodes'])} nodes and {len(workflow['links'])} links")
print("\nModel flow:")
print("  High Noise: LoRA 101 --[190]-> TaylorSeer 121 --[229]-> ModelSampling 104")
print("  Low Noise:  LoRA 102 --[189]-> TaylorSeer 122 --[230]-> ModelSampling 103")

