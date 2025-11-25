#!/usr/bin/env python3
"""
Create PNG-output fork of the main workflow and integrate FILM interpolation

This creates a new workflow that:
1. Outputs PNG frames instead of video
2. Saves to frames/ directory
3. Integrates with FILM interpolation pipeline
"""

import json
import sys
from pathlib import Path

# Paths
input_workflow = "user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json"
output_workflow = "user/default/workflows/video_wan2_2_14B_i2v_PNG_FILM.json"

print("=" * 70)
print("Creating PNG + FILM Workflow Fork")
print("=" * 70)

# Load the workflow
with open(input_workflow, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

print(f"\n[INFO] Loaded workflow from: {input_workflow}")
print(f"[INFO] Workflow ID: {workflow.get('id', 'N/A')}")

# ComfyUI workflow format: {"id": ..., "nodes": [...], "links": [...], ...}
nodes = workflow['nodes']

print(f"[INFO] Total nodes: {len(nodes)}")

# Find SaveVideo node
save_video_node = None
save_video_idx = None

for idx, node in enumerate(nodes):
    if node.get('type') == 'SaveVideo':
        save_video_node = node
        save_video_idx = idx
        print(f"\n[FOUND] SaveVideo node: Index {idx}, ID {node['id']}")
        print(f"  Type: {node['type']}")
        print(f"  Widgets: {node.get('widgets_values', [])}")
        break

if not save_video_node:
    print("[ERROR] Could not find SaveVideo node!")
    sys.exit(1)

# Get the input link
video_input_link = None
for inp in save_video_node['inputs']:
    if inp['name'] == 'video' and 'link' in inp:
        video_input_link = inp['link']
        break

print(f"\n[INFO] Video input link ID: {video_input_link}")

# Get node position and other properties
pos = save_video_node.get('pos', [1690, -250])
size = save_video_node.get('size', [315, 270])
node_id = save_video_node['id']
order = save_video_node.get('order', 40)
flags = save_video_node.get('flags', {})

# Create new SaveImage node - preserve all required ComfyUI node properties
new_node = {
    'id': node_id,
    'type': 'SaveImage',  # Changed from SaveVideo
    'pos': pos,
    'size': size,
    'flags': flags,
    'order': order,
    'mode': 0,
    'inputs': [
        {
            'name': 'images',
            'type': 'IMAGE',
            'link': video_input_link
        }
    ],
    'outputs': [],
    'properties': {
        'Node name for S&R': 'SaveImage'
    },
    'widgets_values': ['frames/video']  # filename_prefix
}

# Replace SaveVideo with SaveImage
nodes[save_video_idx] = new_node

print(f"\n[MODIFIED] Node {node_id} (index {save_video_idx}):")
print(f"  Old: SaveVideo -> MP4")
print(f"  New: SaveImage -> PNG sequence")
print(f"  Output directory: output/frames/")
print(f"  Filename prefix: frames/video")

# Save the new workflow
with open(output_workflow, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, separators=(',', ':'))

print(f"\n[SUCCESS] Created new workflow:")
print(f"  {output_workflow}")

print("\n" + "=" * 70)
print("Workflow Changes Summary")
print("=" * 70)
print("[OK] Output format: MP4 video -> PNG frame sequence")
print("[OK] Output location: output/frames/")
print("[OK] Ready for high-quality FILM interpolation")
print("[OK] No compression before interpolation")
print("\nNext steps:")
print("1. Test the new workflow")
print("2. Update generate_wan22_video.py to use this workflow")
print("3. Add automatic FILM interpolation")
print("=" * 70)

