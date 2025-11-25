import json

with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'r', encoding='utf-8') as f:
    w = json.load(f)

# Find all UNETLoader nodes that are ACTIVE (mode 0)
unet_loaders = [n for n in w['nodes'] if n['type'] == 'UNETLoader' and n.get('mode', 0) == 0]

print(f"Active UNETLoader nodes: {len(unet_loaders)}\n")
for n in unet_loaders:
    model_name = n['widgets_values'][0]
    outputs = [l for l in w['links'] if l[1] == n['id']]
    dest_nodes = [f"Node {l[3]}" for l in outputs]
    print(f"Node {n['id']}: {model_name}")
    print(f"  Outputs to: {dest_nodes}")
    print()

# Check which nodes they connect to
print("\nModel flow:")
for n in unet_loaders:
    outputs = [l for l in w['links'] if l[1] == n['id']]
    for link in outputs:
        dest_node = next((node for node in w['nodes'] if node['id'] == link[3]), None)
        if dest_node:
            print(f"  {n['widgets_values'][0]} -> Node {dest_node['id']} ({dest_node['type']})")

