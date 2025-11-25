import json
import sys

workflow_path = 'user/default/workflows/video_wan2_2_14B_i2v_DELETE_MODEL.json'

try:
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
except FileNotFoundError:
    print(f"Error: Workflow file not found at {workflow_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {workflow_path}")
    sys.exit(1)

# Find the highest existing node ID
max_node_id = 0
for node in workflow.get('nodes', []):
    if node['id'] > max_node_id:
        max_node_id = node['id']

# Find the highest existing link ID
max_link_id = 0
for link in workflow.get('links', []):
    if link[0] > max_link_id:
        max_link_id = link[0]

print(f"Current max node ID: {max_node_id}")
print(f"Current max link ID: {max_link_id}")

# Define new node ID for DeleteModelPassthrough
delete_model_node_id = max_node_id + 1

# Define new link IDs
link_id_1 = max_link_id + 1  # KSampler 86 LATENT output to DeleteModel data input
link_id_2 = max_link_id + 2  # Sage3 Node 117 MODEL output to DeleteModel model input
link_id_3 = max_link_id + 3  # DeleteModel output to KSampler 85 latent_image input

print(f"\nCreating DeleteModelPassthrough node: {delete_model_node_id}")
print(f"Creating links: {link_id_1}, {link_id_2}, {link_id_3}")

# Find the original link from KSampler 86 to KSampler 85
original_link_index = -1
original_link_id = -1
for i, link in enumerate(workflow.get('links', [])):
    # KSampler 86 LATENT output (slot 0) to KSampler 85 latent_image input (slot 3)
    if link[1] == 86 and link[3] == 85 and link[4] == 3:
        original_link_index = i
        original_link_id = link[0]
        break

if original_link_index == -1:
    print("Error: Could not find the link from KSampler 86 to KSampler 85")
    sys.exit(1)

print(f"Found original link {original_link_id}: Node 86 -> Node 85")

# Find the Sage3 Node 117 -> KSampler 86 link
sage_high_link = None
for link in workflow.get('links', []):
    if link[1] == 117 and link[3] == 86 and link[2] == 0:  # Sage3 output slot 0 (MODEL)
        sage_high_link = link
        break

if not sage_high_link:
    print("Error: Could not find Sage3 Node 117 output link to KSampler 86")
    sys.exit(1)

print(f"Found Sage3 high noise link: {sage_high_link[0]}")

# Add DeleteModelPassthrough node
new_node = {
    "id": delete_model_node_id,
    "type": "Delete Model (Passthrough Any)",
    "pos": [1150, 1110],
    "size": [300, 80],
    "flags": {},
    "order": 33,
    "mode": 0,
    "inputs": [
        {"name": "data", "type": "*", "link": original_link_id},  # From KSampler 86 LATENT
        {"name": "model", "type": "MODEL", "link": link_id_2}     # From Sage3 Node 117
    ],
    "outputs": [
        {"name": "*", "type": "*", "links": [link_id_3]}  # To KSampler 85
    ],
    "title": "Delete High Noise Model",
    "properties": {"Node name for S&R": "Delete Model (Passthrough Any)"},
    "widgets_values": []
}
workflow['nodes'].append(new_node)

# Update the original link to point to DeleteModel data input
workflow['links'][original_link_index][3] = delete_model_node_id  # Target node ID
workflow['links'][original_link_index][4] = 0  # Target input index (data input)

# Add new link from Sage3 Node 117 to DeleteModel model input
new_link_sage_to_delete = [
    link_id_2,
    117,  # Source: Sage3 Node (high noise model path)
    0,    # Source output slot (MODEL)
    delete_model_node_id,  # Target: DeleteModel node
    1,    # Target input slot (model input)
    "MODEL"
]
workflow['links'].append(new_link_sage_to_delete)

# Add new link from DeleteModel output to KSampler 85
new_link_delete_to_ksampler = [
    link_id_3,
    delete_model_node_id,  # Source: DeleteModel
    0,   # Source output slot
    85,  # Target: Low Noise KSampler
    3,   # Target input slot (latent_image)
    "LATENT"
]
workflow['links'].append(new_link_delete_to_ksampler)

# Update last_node_id and last_link_id
workflow['last_node_id'] = delete_model_node_id
workflow['last_link_id'] = link_id_3

# Save the updated workflow
with open(workflow_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Workflow updated with DeleteModelPassthrough!")
print(f"\nFlow:")
print(f"  Sage3 Node 117 (High Noise Model Path) -> [{link_id_2}] -> DeleteModel {delete_model_node_id} (model input)")
print(f"  KSampler 86 (High Pass) -> [{original_link_id}] -> DeleteModel {delete_model_node_id} (data input)")
print(f"  DeleteModel {delete_model_node_id} -> [{link_id_3}] -> KSampler 85 (Low Pass)")
print(f"\nThe high noise model will be COMPLETELY deleted from VRAM and RAM after the first pass,")
print(f"freeing up ~13GB for the low noise model to load fully without offloading!")
print(f"\nNow restart ComfyUI and test with 81 frames to see if the 845MB offload is eliminated!")
