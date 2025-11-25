import json
import uuid

# Use the CLEAN workflow (NO_UNLOAD version)
input_path = 'user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json'
output_path = 'user/default/workflows/WAN22_DELETEMODEL_FIXED.json'

with open(input_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

print(f"Starting with clean workflow")
print(f"Nodes: {len(workflow['nodes'])}")
print(f"Links: {len(workflow['links'])}")

# Find link 170 (KSampler 86 -> KSampler 85)
link170_idx = None
for idx, link in enumerate(workflow['links']):
    if link[0] == 170 and link[1] == 86 and link[3] == 85:
        link170_idx = idx
        break

if link170_idx is None:
    print("ERROR: Could not find link 170 from KSampler 86 to KSampler 85")
    import sys
    sys.exit(1)

print(f"Found link 170 at index {link170_idx}: {workflow['links'][link170_idx]}")

# Modify link 170 to go to DeleteModel node (119) instead of KSampler 85
workflow['links'][link170_idx][3] = 119  # Target node
workflow['links'][link170_idx][4] = 0    # Target input slot (data)

print(f"Modified link 170: KSampler 86 -> DeleteModel 119")

# Add link 226: Sage3 117 -> DeleteModel 119 (model input)
workflow['links'].append([226, 117, 0, 119, 1, "MODEL"])
print(f"Added link 226: Sage3 117 -> DeleteModel 119")

# Add link 227: DeleteModel 119 -> KSampler 85
workflow['links'].append([227, 119, 0, 85, 3, "LATENT"])
print(f"Added link 227: DeleteModel 119 -> KSampler 85")

# Create DeleteModel node
delete_node = {
    "id": 119,
    "type": "DeleteModelPassthrough",
    "pos": [1300, 50],
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

workflow['nodes'].append(delete_node)
print(f"Added DeleteModel node 119")

# Update KSampler 85's latent_image input to reference link 227
for node in workflow['nodes']:
    if node['id'] == 85:
        for inp in node['inputs']:
            if inp['name'] == 'latent_image':
                inp['link'] = 227
                print(f"Updated KSampler 85 latent_image input to link 227")
                break
        break

# CRITICAL FIX: Add link 226 to Node 117's outputs
for node in workflow['nodes']:
    if node['id'] == 117:
        # Find the MODEL output
        for output in node['outputs']:
            if output['type'] == 'MODEL':
                # Add link 226 to this output's links
                if 'links' not in output or output['links'] is None:
                    output['links'] = []
                if 226 not in output['links']:
                    output['links'].append(226)
                print(f"Added link 226 to Node 117 MODEL output")
                break
        break

# Update metadata
workflow['last_node_id'] = 119
workflow['last_link_id'] = 227
workflow['id'] = str(uuid.uuid4())
workflow['version'] = 0.4

# Save
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Created: {output_path}")
print(f"Nodes: {len(workflow['nodes'])}")
print(f"Links: {len(workflow['links'])}")
print(f"\nConnection flow:")
print(f"  KSampler 86 --[170]--> DeleteModel 119 --[227]--> KSampler 85")
print(f"  Sage3 117 --[226]--> DeleteModel 119 (model)")
print(f"\nNode 117 outputs: {[node['outputs'] for node in workflow['nodes'] if node['id'] == 117]}")

