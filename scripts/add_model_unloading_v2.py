"""
PROPERLY add model unloading nodes between two-pass samplers
"""
import json

# Load workflow
with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find actual max IDs
max_node_id = max(n['id'] for n in workflow['nodes'])
max_link_id = max(l[0] for l in workflow['links'])

print(f"Current max node ID: {max_node_id}")
print(f"Current max link ID: {max_link_id}")

# Create new node IDs
clean_gpu_id = max_node_id + 1
clear_cache_id = max_node_id + 2

# Create new link IDs
link_86_to_clean = max_link_id + 1
link_clean_to_clear = max_link_id + 2  
link_clear_to_85 = max_link_id + 3

print(f"\nCreating nodes: {clean_gpu_id}, {clear_cache_id}")
print(f"Creating links: {link_86_to_clean}, {link_clean_to_clear}, {link_clear_to_85}")

# Find link 170 (from node 86, output 0, to node 85, input 3)
found_170 = False
for link in workflow['links']:
    if link[0] == 170:  # link ID
        print(f"\nFound link 170: {link}")
        # Change it to go to cleanGpu instead
        link[3] = clean_gpu_id  # destination node
        link[4] = 0  # input index
        found_170 = True
        break

if not found_170:
    print("ERROR: Link 170 not found!")
    exit(1)

# Update node 85's latent_image input to come from clearCache
found_85 = False
for node in workflow['nodes']:
    if node['id'] == 85:
        for inp in node['inputs']:
            if inp.get('link') == 170:
                print(f"Updating node 85 input from link 170 to {link_clear_to_85}")
                inp['link'] = link_clear_to_85
                found_85 = True
                break

if not found_85:
    print("ERROR: Node 85 with link 170 not found!")
    exit(1)

# Create cleanGpuUsed node
clean_node = {
    "id": clean_gpu_id,
    "type": "easy cleanGpuUsed",
    "pos": [1650, 350],
    "size": [220, 26],
    "flags": {},
    "order": 28,
    "mode": 0,
    "inputs": [{
        "name": "anything",
        "type": "*",
        "link": 170
    }],
    "outputs": [{
        "name": "output", 
        "type": "*",
        "links": [link_clean_to_clear]
    }],
    "title": "Unload High Noise Model",
    "properties": {
        "Node name for S&R": "easy cleanGpuUsed",
        "cnr_id": "comfyui-easy-use",
        "ver": "1.3.1"
    },
    "widgets_values": [],
    "color": "#A88",
    "bgcolor": "#C99"
}

# Create clearCacheAll node  
clear_node = {
    "id": clear_cache_id,
    "type": "easy clearCacheAll",
    "pos": [1650, 420],
    "size": [220, 26],
    "flags": {},
    "order": 29,
    "mode": 0,
    "inputs": [{
        "name": "anything",
        "type": "*",
        "link": link_clean_to_clear
    }],
    "outputs": [{
        "name": "output",
        "type": "*",
        "links": [link_clear_to_85]
    }],
    "title": "Clear Cache",
    "properties": {
        "Node name for S&R": "easy clearCacheAll",
        "cnr_id": "comfyui-easy-use",
        "ver": "1.3.1"
    },
    "widgets_values": [],
    "color": "#A88",
    "bgcolor": "#C99"
}

# Add nodes
workflow['nodes'].append(clean_node)
workflow['nodes'].append(clear_node)
print(f"\nAdded nodes {clean_gpu_id} and {clear_cache_id}")

# Add new links
workflow['links'].append([link_clean_to_clear, clean_gpu_id, 0, clear_cache_id, 0, "*"])
workflow['links'].append([link_clear_to_85, clear_cache_id, 0, 85, 3, "LATENT"])
print(f"Added links {link_clean_to_clear} and {link_clear_to_85}")

# Update last IDs
workflow['last_node_id'] = clear_cache_id
workflow['last_link_id'] = link_clear_to_85

# Save
with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, separators=(',', ':'))

print("\n[SUCCESS] Workflow updated!")
print(f"Flow: Node 86 -> [{170}] -> Node {clean_gpu_id} -> [{link_clean_to_clear}] -> Node {clear_cache_id} -> [{link_clear_to_85}] -> Node 85")

