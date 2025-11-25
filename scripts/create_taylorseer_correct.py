import json
import uuid
import time

# Load base workflow
base_path = "user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json"
with open(base_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find key nodes
node_101 = None  # LoRA High Noise
node_102 = None  # LoRA Low Noise
node_103 = None  # ModelSampling Low Noise
node_104 = None  # ModelSampling High Noise

for node in workflow['nodes']:
    if node['id'] == 101:
        node_101 = node
    elif node['id'] == 102:
        node_102 = node
    elif node['id'] == 103:
        node_103 = node
    elif node['id'] == 104:
        node_104 = node

# Verify we found them
if not all([node_101, node_102, node_103, node_104]):
    print("ERROR: Could not find required nodes")
    exit(1)

print(f"Found Node 101 (LoRA High): outputs link {node_101['outputs'][0]['links']}")
print(f"Found Node 102 (LoRA Low): outputs link {node_102['outputs'][0]['links']}")
print(f"Found Node 103 (ModelSampling Low): expects input link {node_103['inputs'][0]['link']}")
print(f"Found Node 104 (ModelSampling High): expects input link {node_104['inputs'][0]['link']}")

# Current links
link_101_to_104 = node_101['outputs'][0]['links'][0]  # Should be 190
link_102_to_103 = node_102['outputs'][0]['links'][0]  # Should be 189

print(f"\nCurrent connections:")
print(f"  LoRA 101 --[{link_101_to_104}]--> ModelSampling 104")
print(f"  LoRA 102 --[{link_102_to_103}]--> ModelSampling 103")

# Find max IDs
max_node_id = max(node['id'] for node in workflow['nodes'])
max_link_id = max(link[0] for link in workflow['links'])

print(f"\nMax node ID: {max_node_id}, Max link ID: {max_link_id}")

# Create new node IDs and link IDs
taylorseer_high_id = max_node_id + 1
taylorseer_low_id = max_node_id + 2
link_101_to_ts_high = link_101_to_104  # REUSE existing link 190
link_102_to_ts_low = link_102_to_103   # REUSE existing link 189
link_ts_high_to_104 = max_link_id + 1  # New link 229
link_ts_low_to_103 = max_link_id + 2   # New link 230

print(f"\nNew nodes: {taylorseer_high_id}, {taylorseer_low_id}")
print(f"New links: {link_ts_high_to_104}, {link_ts_low_to_103}")

# Create TaylorSeerLite nodes
taylorseer_high = {
    "id": taylorseer_high_id,
    "type": "TaylorSeerLite",
    "pos": [550, -223],
    "size": [250, 106],
    "flags": {},
    "order": node_101['order'] + 1,
    "mode": 0,
    "inputs": [
        {"name": "model", "type": "MODEL", "link": link_101_to_ts_high}
    ],
    "outputs": [
        {"name": "MODEL", "type": "MODEL", "links": [link_ts_high_to_104], "slot_index": 0}
    ],
    "title": "TaylorSeer High Noise",
    "properties": {"Node name for S&R": "TaylorSeerLite"},
    "widgets_values": ["wanvideo", 5, 1]
}

taylorseer_low = {
    "id": taylorseer_low_id,
    "type": "TaylorSeerLite",
    "pos": [550, -93],
    "size": [250, 106],
    "flags": {},
    "order": node_102['order'] + 1,
    "mode": 0,
    "inputs": [
        {"name": "model", "type": "MODEL", "link": link_102_to_ts_low}
    ],
    "outputs": [
        {"name": "MODEL", "type": "MODEL", "links": [link_ts_low_to_103], "slot_index": 0}
    ],
    "title": "TaylorSeer Low Noise",
    "properties": {"Node name for S&R": "TaylorSeerLite"},
    "widgets_values": ["wanvideo", 5, 1]
}

# Add nodes to workflow
workflow['nodes'].append(taylorseer_high)
workflow['nodes'].append(taylorseer_low)

# Update existing links in the links array
for i, link in enumerate(workflow['links']):
    # Find link 190 (LoRA 101 -> ModelSampling 104) and change target to TaylorSeer
    if link[0] == link_101_to_ts_high:
        workflow['links'][i] = [link_101_to_ts_high, 101, 0, taylorseer_high_id, 0, "MODEL"]
        print(f"\nUpdated link {link_101_to_ts_high}: LoRA 101 -> TaylorSeer {taylorseer_high_id}")
    # Find link 189 (LoRA 102 -> ModelSampling 103) and change target to TaylorSeer
    elif link[0] == link_102_to_ts_low:
        workflow['links'][i] = [link_102_to_ts_low, 102, 0, taylorseer_low_id, 0, "MODEL"]
        print(f"Updated link {link_102_to_ts_low}: LoRA 102 -> TaylorSeer {taylorseer_low_id}")

# Add new links from TaylorSeer to ModelSampling
workflow['links'].append([link_ts_high_to_104, taylorseer_high_id, 0, 104, 0, "MODEL"])
workflow['links'].append([link_ts_low_to_103, taylorseer_low_id, 0, 103, 0, "MODEL"])

print(f"Added link {link_ts_high_to_104}: TaylorSeer {taylorseer_high_id} -> ModelSampling 104")
print(f"Added link {link_ts_low_to_103}: TaylorSeer {taylorseer_low_id} -> ModelSampling 103")

# Update ModelSampling nodes to expect new input links
node_104['inputs'][0]['link'] = link_ts_high_to_104
node_103['inputs'][0]['link'] = link_ts_low_to_103

print(f"\nUpdated ModelSampling 104 input: link {link_ts_high_to_104}")
print(f"Updated ModelSampling 103 input: link {link_ts_low_to_103}")

# Update workflow metadata
workflow['last_node_id'] = taylorseer_low_id
workflow['last_link_id'] = link_ts_low_to_103
workflow['id'] = str(uuid.uuid4())
workflow['version'] = time.time()

# Save new workflow
output_path = f"user/default/workflows/TAYLORSEER_FINAL.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Created: {output_path}")
print(f"Workflow ID: {workflow['id']}")
print(f"Nodes: {len(workflow['nodes'])}, Links: {len(workflow['links'])}")
print(f"\nFinal flow:")
print(f"  LoRA 101 --[{link_101_to_ts_high}]--> TaylorSeer {taylorseer_high_id} --[{link_ts_high_to_104}]--> ModelSampling 104")
print(f"  LoRA 102 --[{link_102_to_ts_low}]--> TaylorSeer {taylorseer_low_id} --[{link_ts_low_to_103}]--> ModelSampling 103")






