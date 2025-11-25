import json
import sys

# Load the clean NO_UNLOAD workflow
workflow_path = 'user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json'
output_path = 'user/default/workflows/video_wan2_2_DELETEMODEL_FINAL.json'

with open(workflow_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find highest node and link IDs
max_node_id = max(node['id'] for node in workflow['nodes'])
max_link_id = max(link[0] for link in workflow['links'])

print(f"Max node ID: {max_node_id}")
print(f"Max link ID: {max_link_id}")

# Define new IDs
delete_node_id = max_node_id + 1
link_model_to_delete = max_link_id + 1
link_delete_to_ksampler = max_link_id + 2

print(f"New DeleteModel node ID: {delete_node_id}")
print(f"New link IDs: {link_model_to_delete}, {link_delete_to_ksampler}")

# Find the link from KSampler 86 to KSampler 85
original_link = None
original_link_idx = None
for idx, link in enumerate(workflow['links']):
    if link[1] == 86 and link[3] == 85 and link[4] == 3:  # KS86 -> KS85 latent_image
        original_link = link
        original_link_idx = idx
        break

if not original_link:
    print("ERROR: Could not find link from KSampler 86 to KSampler 85")
    sys.exit(1)

print(f"Found original link {original_link[0]}: KSampler 86 -> KSampler 85")

# Update the original link to point to DeleteModel instead
workflow['links'][original_link_idx][3] = delete_node_id  # Target: DeleteModel
workflow['links'][original_link_idx][4] = 0  # Target input: data

print(f"Updated link {original_link[0]} to: KSampler 86 -> DeleteModel {delete_node_id}")

# Add link from Sage3 Node 117 to DeleteModel
workflow['links'].append([
    link_model_to_delete,
    117,  # Source: Sage3 node (bypassed, passes model through)
    0,    # Source output slot
    delete_node_id,  # Target: DeleteModel
    1,    # Target input: model
    "MODEL"
])

print(f"Added link {link_model_to_delete}: Sage3 117 -> DeleteModel {delete_node_id}")

# Add link from DeleteModel to KSampler 85
workflow['links'].append([
    link_delete_to_ksampler,
    delete_node_id,  # Source: DeleteModel
    0,    # Source output slot
    85,   # Target: KSampler 85
    3,    # Target input: latent_image
    "LATENT"
])

print(f"Added link {link_delete_to_ksampler}: DeleteModel {delete_node_id} -> KSampler 85")

# Create the DeleteModel node
delete_node = {
    "id": delete_node_id,
    "type": "DeleteModelPassthrough",
    "pos": [1150, 100],
    "size": [320, 80],
    "flags": {},
    "order": 32,
    "mode": 0,
    "inputs": [
        {"name": "data", "type": "*", "link": original_link[0]},
        {"name": "model", "type": "MODEL", "link": link_model_to_delete}
    ],
    "outputs": [
        {"name": "*", "type": "*", "links": [link_delete_to_ksampler]}
    ],
    "title": "Delete High Noise Model",
    "properties": {"Node name for S&R": "DeleteModelPassthrough"},
    "widgets_values": [],
    "color": "#A88",
    "bgcolor": "#C99"
}

workflow['nodes'].append(delete_node)

# Update metadata
workflow['last_node_id'] = delete_node_id
workflow['last_link_id'] = link_delete_to_ksampler

# Generate new workflow ID
import uuid
workflow['id'] = str(uuid.uuid4())

# Save
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Created: {output_path}")
print(f"Node {delete_node_id}: DeleteModelPassthrough")
print(f"  Input 1 (data): Link {original_link[0]} from KSampler 86")
print(f"  Input 2 (model): Link {link_model_to_delete} from Sage3 117")
print(f"  Output: Link {link_delete_to_ksampler} to KSampler 85")
print("\nVerification:")
print(f"  Total nodes: {len(workflow['nodes'])}")
print(f"  Total links: {len(workflow['links'])}")
print(f"  Workflow ID: {workflow['id']}")

