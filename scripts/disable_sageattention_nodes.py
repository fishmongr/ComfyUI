import json
import sys

workflow_path = 'user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json'

try:
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
except FileNotFoundError:
    print(f"Error: Workflow file not found at {workflow_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {workflow_path}")
    sys.exit(1)

# Find and bypass Sage3AttentionOnlySwitch nodes (117 and 118)
sage_nodes = []
for node in workflow['nodes']:
    if node.get('type') == 'Sage3AttentionOnlySwitch':
        sage_nodes.append(node)
        # Set mode to 4 (bypassed)
        node['mode'] = 4
        print(f"Bypassed Sage3AttentionOnlySwitch Node {node['id']}")

if not sage_nodes:
    print("No SageAttention nodes found")
else:
    # Save the updated workflow
    with open(workflow_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SUCCESS] Bypassed {len(sage_nodes)} SageAttention nodes")
    print("SageAttention is now disabled - models will use PyTorch's native attention")
    print("\nThis is fine because:")
    print("  - PyTorch SDPA with FlashAttention is already enabled by default")
    print("  - RTX 5090 has native FlashAttention support")
    print("  - SageAttention3 has build issues on your system")



