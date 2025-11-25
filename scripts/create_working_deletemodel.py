import json
import uuid

# Load the workflow that already has nodes 119-120 (the cache nodes)
workflow_path = 'user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json'
output_path = 'user/default/workflows/WAN22_DELETEMODEL_WORKING.json'

with open(workflow_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find and remove nodes 119 and 120
workflow['nodes'] = [n for n in workflow['nodes'] if n['id'] not in [119, 120]]

# Find and remove links that referenced nodes 119 or 120
workflow['links'] = [l for l in workflow['links'] if l[1] not in [119, 120] and l[3] not in [119, 120]]

print(f"Removed old nodes 119-120")
print(f"Remaining nodes: {len(workflow['nodes'])}")
print(f"Remaining links: {len(workflow['links'])}")

# Now find link 170 (KSampler 86 -> originally went to node 119, then to 85)
link170 = None
for idx, link in enumerate(workflow['links']):
    if link[0] == 170:
        link170 = (idx, link)
        break

if not link170:
    print("ERROR: Link 170 not found!")
    import sys
    sys.exit(1)

idx170, link170_data = link170
print(f"Found link 170: {link170_data}")
print(f"  Currently connects: Node {link170_data[1]} -> Node {link170_data[3]}")

# Create new DeleteModel node (ID 119)
delete_node = {
    "id": 119,
    "type": "DeleteModelPassthrough",
    "pos": [1300, 100],
    "size": [320, 80],
    "flags": {},
    "order": 32,
    "mode": 0,
    "inputs": [
        {"name": "data", "type": "*", "link": 170},
        {"name": "model", "type": "MODEL", "link": 226}
    ],
    "outputs": [
        {"name": "*", "type": "*", "links": [227]}
    ],
    "title": "Delete High Noise Model",
    "properties": {"Node name for S&R": "DeleteModelPassthrough"},
    "widgets_values": [],
    "color": "#A88",
    "bgcolor": "#C99"
}

# Update link 170 to point to DeleteModel node
workflow['links'][idx170][3] = 119  # Target node: DeleteModel
workflow['links'][idx170][4] = 0    # Target input: data

print(f"Updated link 170: Node 86 -> Node 119 (DeleteModel)")

# Add link 226: Sage3 Node 117 -> DeleteModel
workflow['links'].append([226, 117, 0, 119, 1, "MODEL"])
print(f"Added link 226: Node 117 (Sage3) -> Node 119 (DeleteModel)")

# Add link 227: DeleteModel -> KSampler 85
workflow['links'].append([227, 119, 0, 85, 3, "LATENT"])
print(f"Added link 227: Node 119 (DeleteModel) -> Node 85 (KSampler)")

# Add the DeleteModel node
workflow['nodes'].append(delete_node)

# Update metadata
workflow['last_node_id'] = 119
workflow['last_link_id'] = 227
workflow['id'] = str(uuid.uuid4())
workflow['version'] = 0.4

# Save
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Created: {output_path}")
print(f"Total nodes: {len(workflow['nodes'])}")
print(f"Total links: {len(workflow['links'])}")
print(f"Workflow ID: {workflow['id']}")
print(f"\nFlow:")
print(f"  KSampler 86 --[Link 170]--> DeleteModel 119 --[Link 227]--> KSampler 85")
print(f"  Sage3 117 ----[Link 226]--> DeleteModel 119")

