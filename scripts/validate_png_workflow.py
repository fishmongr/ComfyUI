#!/usr/bin/env python3
"""Validate the PNG workflow"""
import json

workflow_path = "user/default/workflows/video_wan2_2_14B_i2v_PNG_FILM.json"

with open(workflow_path, 'r') as f:
    workflow = json.load(f)

# Find node 108
node108 = None
for node in workflow['nodes']:
    if node['id'] == 108:
        node108 = node
        break

if not node108:
    print("[ERROR] Node 108 not found!")
    exit(1)

print("Node 108 validation:")
print(f"  id: {node108.get('id')}")
print(f"  type: {node108.get('type')}")
print(f"  pos: {node108.get('pos')}")
print(f"  size: {node108.get('size')}")
print(f"  flags: {node108.get('flags')}")
print(f"  order: {node108.get('order')}")
print(f"  mode: {node108.get('mode')}")
print(f"  inputs: {len(node108.get('inputs', []))} inputs")
print(f"  outputs: {len(node108.get('outputs', []))} outputs")
print(f"  properties: {node108.get('properties')}")
print(f"  widgets_values: {node108.get('widgets_values')}")

required_fields = ['id', 'type', 'pos', 'size', 'flags', 'order', 'mode', 'inputs', 'outputs', 'properties', 'widgets_values']
missing = [f for f in required_fields if f not in node108]

if missing:
    print(f"\n[ERROR] Missing fields: {missing}")
else:
    print("\n[OK] All required fields present")

# Check for 'class_type' which shouldn't be there in this format
if 'class_type' in node108:
    print(f"[WARNING] Has 'class_type' field (should be 'type')")

