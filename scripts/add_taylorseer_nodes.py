import json
import uuid

# Load the base workflow
input_path = "user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json"
output_path = "user/default/workflows/video_wan2_2_14B_i2v_TAYLORSEER.json"

with open(input_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

print(f"Loaded workflow with {len(workflow['nodes'])} nodes and {len(workflow['links'])} links")

# Find the highest node and link IDs
max_node_id = max(node['id'] for node in workflow['nodes'])
max_link_id = max(link[0] for link in workflow['links'])

print(f"Max node ID: {max_node_id}, Max link ID: {max_link_id}")

# We need to insert TaylorSeerLite nodes AFTER the LoRA loaders
# Current flow: UNET (95) -> LoRA (101) -> ModelSampling (104) -> Sage3 (117) -> KSampler (86)
# New flow:     UNET (95) -> LoRA (101) -> TaylorSeer (121) -> ModelSampling (104) -> Sage3 (117) -> KSampler (86)

# High Noise Model Chain
# Find link from LoRA 101 to ModelSampling 104 (link 190)
# We'll insert TaylorSeer node 121 between them

# Low Noise Model Chain  
# Find link from LoRA 102 to ModelSampling 103 (link 189)
# We'll insert TaylorSeer node 122 between them

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
        {"name": "MODEL", "type": "MODEL", "links": [229]}
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
        {"name": "MODEL", "type": "MODEL", "links": [230]}
    ],
    "title": "TaylorSeerLite (Low Noise)",
    "properties": {"Node name for S&R": "TaylorSeerLite"},
    "widgets_values": ["wanvideo", 5, 1, 1, 50],
    "color": "#2a363b",
    "bgcolor": "#3f5159"
}

# Add the new nodes
workflow['nodes'].append(taylor_high_node)
workflow['nodes'].append(taylor_low_node)

# Update link 190: LoRA 101 -> TaylorSeer 121 (keep existing link, it goes to TaylorSeer now)
# Link 190 already goes from node 101 to "somewhere", we just need TaylorSeer to receive it
# The link is already correct in the node definition above

# Update link 189: LoRA 102 -> TaylorSeer 122 (keep existing link)
# Same as above

# Add new link 229: TaylorSeer 121 -> ModelSampling 104
workflow['links'].append([229, 121, 0, 104, 0, "MODEL"])

# Add new link 230: TaylorSeer 122 -> ModelSampling 103
workflow['links'].append([230, 122, 0, 103, 0, "MODEL"])

# Update ModelSampling node 104 to receive from TaylorSeer 121 instead of LoRA 101
for node in workflow['nodes']:
    if node['id'] == 104:
        for inp in node['inputs']:
            if inp['name'] == 'model' and inp['link'] == 190:
                inp['link'] = 229
                print("Updated ModelSampling 104 input: link 190 -> 229")
                
# Update ModelSampling node 103 to receive from TaylorSeer 122 instead of LoRA 102
for node in workflow['nodes']:
    if node['id'] == 103:
        for inp in node['inputs']:
            if inp['name'] == 'model' and inp['link'] == 189:
                inp['link'] = 230
                print("Updated ModelSampling 103 input: link 189 -> 230")

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
print("  High Noise: UNET 95 -> LoRA 101 -> TaylorSeer 121 -> ModelSampling 104 -> Sage3 117 -> KSampler 86")
print("  Low Noise:  UNET 96 -> LoRA 102 -> TaylorSeer 122 -> ModelSampling 103 -> Sage3 118 -> KSampler 85")

