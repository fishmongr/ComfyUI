#!/usr/bin/env python3
"""
Fix the PNG workflow to connect SaveImage to IMAGE source instead of VIDEO
"""

import json

workflow_path = "user/default/workflows/video_wan2_2_14B_i2v_PNG_FILM.json"

print("Fixing PNG workflow node connections...")

# Load workflow
with open(workflow_path, 'r') as f:
    workflow = json.load(f)

# Find nodes
nodes = workflow['nodes']

save_image_node = None
save_image_idx = None
vae_decode_node = None

for idx, node in enumerate(nodes):
    if node['id'] == 108:  # SaveImage (formerly SaveVideo)
        save_image_node = node
        save_image_idx = idx
    elif node['id'] == 87:  # VAEDecode
        vae_decode_node = node

print(f"Found SaveImage node (ID 108)")
print(f"Found VAEDecode node (ID 87)")

# Get the IMAGE link from VAEDecode
image_link = vae_decode_node['outputs'][0]['links'][0]  # Link 182
print(f"IMAGE link from VAEDecode: {image_link}")

# Update SaveImage to connect to IMAGE instead of VIDEO
save_image_node['inputs'][0]['link'] = image_link

print(f"Updated SaveImage input link: {save_image_node['inputs'][0]['link']}")

# Save workflow
with open(workflow_path, 'w') as f:
    json.dump(workflow, f, separators=(',', ':'))

print(f"\n[SUCCESS] Fixed workflow saved to: {workflow_path}")
print("[INFO] SaveImage now connects directly to VAEDecode output (IMAGE)")



