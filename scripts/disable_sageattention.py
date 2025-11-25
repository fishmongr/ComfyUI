#!/usr/bin/env python3
"""Disable SageAttention3 nodes in the workflow."""

import json
import sys

workflow_path = "user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json"

# Load workflow
with open(workflow_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find and modify SageAttention3 nodes
sage_nodes_found = 0
for node in data['nodes']:
    if 'Sage' in node.get('type', ''):
        print(f"Found Node {node['id']}: {node['type']}")
        print(f"  Current widgets_values: {node.get('widgets_values', [])}")
        
        # Disable SageAttention3 (first value is 'enable', second is 'print_backend')
        if 'widgets_values' in node:
            node['widgets_values'][0] = False  # Disable
            print(f"  Updated widgets_values: {node['widgets_values']}")
            sage_nodes_found += 1

if sage_nodes_found > 0:
    # Save modified workflow
    with open(workflow_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print(f"\nDisabled SageAttention3 on {sage_nodes_found} nodes")
    print(f"Workflow saved: {workflow_path}")
else:
    print("No SageAttention3 nodes found in workflow")
    sys.exit(1)


