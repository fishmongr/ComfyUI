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

# Find Node 119 and fix its type
node_119 = None
for node in workflow['nodes']:
    if node['id'] == 119:
        node_119 = node
        break

if not node_119:
    print("Error: Node 119 not found")
    sys.exit(1)

print(f"Current type: {node_119['type']}")

# Fix the type name - use the internal class name, not the display name
node_119['type'] = 'DeleteModelPassthrough'
node_119['properties']['Node name for S&R'] = 'DeleteModelPassthrough'

print(f"Updated type: {node_119['type']}")

# Save the corrected workflow
with open(workflow_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n✅ [SUCCESS] Fixed Node 119 type name!")
print(f"Node 119 is now: DeleteModelPassthrough (internal class name)")
print(f"Display name will be: Delete Model (Passthrough Any)")

