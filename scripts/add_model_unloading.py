"""
Add model unloading nodes between two-pass samplers to prevent VRAM offloading
"""
import json
import sys

# Load workflow
with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the highest node and link IDs
max_node_id = workflow['last_node_id']
max_link_id = workflow['last_link_id']

# Create new node IDs
clean_gpu_node_id = max_node_id + 1
clear_cache_node_id = max_node_id + 2

# Create new link IDs  
link_86_to_clean = max_link_id + 1  # From KSampler 86 to cleanGpuUsed
link_clean_to_clear = max_link_id + 2  # From cleanGpuUsed to clearCacheAll
link_clear_to_85 = max_link_id + 3  # From clearCacheAll to KSampler 85

# Node 86 (High Noise KSampler) currently outputs link 170 to node 85
# We need to intercept this

# Find and update link 170 to point to our clean_gpu node instead
for link in workflow['links']:
    if link[0] == 170:  # This is the link from node 86 to node 85
        link[3] = clean_gpu_node_id  # Change destination to cleanGpuUsed
        link[4] = 0  # Input index 0 on cleanGpuUsed
        break

# Update node 85's input to come from clearCacheAll instead of node 86
for node in workflow['nodes']:
    if node['id'] == 85:  # Low Noise KSampler
        for input_conn in node['inputs']:
            if input_conn.get('link') == 170:
                input_conn['link'] = link_clear_to_85

# Create the easy cleanGpuUsed node (between KSampler 86 and clearCacheAll)
clean_gpu_node = {
    "id": clean_gpu_node_id,
    "type": "easy cleanGpuUsed",
    "pos": [1650, 350],  # Position between the two KSamplers
    "size": [220, 26],
    "flags": {},
    "order": 28,  # After node 86 (order 27), before node 85 (order 29)
    "mode": 0,
    "inputs": [
        {
            "name": "anything",
            "type": "*",
            "link": 170  # Input from KSampler 86
        }
    ],
    "outputs": [
        {
            "name": "output",
            "type": "*",
            "links": [link_clean_to_clear]  # Output to clearCacheAll
        }
    ],
    "title": "🔥 Unload High Noise Model",
    "properties": {
        "Node name for S&R": "easy cleanGpuUsed",
        "cnr_id": "comfyui-easy-use",
        "ver": "1.3.1",
        "ue_properties": {
            "widget_ue_connectable": {},
            "version": "7.1",
            "input_ue_unconnectable": {}
        }
    },
    "widgets_values": [],
    "color": "#A88",
    "bgcolor": "#C99"
}

# Create the easy clearCacheAll node (between cleanGpuUsed and KSampler 85)
clear_cache_node = {
    "id": clear_cache_node_id,
    "type": "easy clearCacheAll",
    "pos": [1650, 420],  # Position below cleanGpuUsed
    "size": [220, 26],
    "flags": {},
    "order": 29,  # After cleanGpuUsed, before the updated node 85
    "mode": 0,
    "inputs": [
        {
            "name": "anything",
            "type": "*",
            "link": link_clean_to_clear  # Input from cleanGpuUsed
        }
    ],
    "outputs": [
        {
            "name": "output",
            "type": "*",
            "links": [link_clear_to_85]  # Output to KSampler 85
        }
    ],
    "title": "🧹 Clear Cache",
    "properties": {
        "Node name for S&R": "easy clearCacheAll",
        "cnr_id": "comfyui-easy-use",
        "ver": "1.3.1",
        "ue_properties": {
            "widget_ue_connectable": {},
            "version": "7.1",
            "input_ue_unconnectable": {}
        }
    },
    "widgets_values": [],
    "color": "#A88",
    "bgcolor": "#C99"
}

# Add new nodes
workflow['nodes'].append(clean_gpu_node)
workflow['nodes'].append(clear_cache_node)

# Add new links
workflow['links'].append([link_clean_to_clear, clean_gpu_node_id, 0, clear_cache_node_id, 0, "*"])
workflow['links'].append([link_clear_to_85, clear_cache_node_id, 0, 85, 3, "LATENT"])

# Update node 85's order to be after our new nodes
for node in workflow['nodes']:
    if node['id'] == 85:
        node['order'] = 30  # Was 29, now after clearCacheAll

# Update last IDs
workflow['last_node_id'] = clear_cache_node_id
workflow['last_link_id'] = link_clear_to_85

# Save updated workflow
with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=None, separators=(',', ':'))

print("[OK] Successfully added model unloading nodes!")
print(f"   - Added 'easy cleanGpuUsed' (node {clean_gpu_node_id})")
print(f"   - Added 'easy clearCacheAll' (node {clear_cache_node_id})")
print(f"   - Positioned between High Noise Pass and Low Noise Pass")
print(f"\n[TARGET] This should fix the 61-frame offloading issue!")

