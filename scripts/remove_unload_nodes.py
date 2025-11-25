"""
Remove the unload nodes from workflow for testing
"""
import json

with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the nodes
clean_gpu = next((n for n in workflow['nodes'] if n['type'] == 'easy cleanGpuUsed'), None)
clear_cache = next((n for n in workflow['nodes'] if n['type'] == 'easy clearCacheAll'), None)

if not clean_gpu or not clear_cache:
    print("Unload nodes not found!")
    exit(1)

print(f"Found nodes: {clean_gpu['id']}, {clear_cache['id']}")

# Find link 170 (from KSampler 86)
link_170 = next((l for l in workflow['links'] if l[0] == 170), None)
if not link_170:
    print("Link 170 not found!")
    exit(1)

print(f"Link 170 currently goes to: Node {link_170[3]}")

# Find the link from clearCache to KSampler 85
final_link = next((l for l in workflow['links'] if l[1] == clear_cache['id']), None)
if final_link:
    # Reconnect KSampler 86 directly to KSampler 85
    link_170[3] = 85  # destination node
    link_170[4] = 3   # input index (latent_image)
    print(f"Reconnected: Node 86 -> Node 85 (bypassing unload nodes)")

# Update KSampler 85's input
for node in workflow['nodes']:
    if node['id'] == 85:
        for inp in node['inputs']:
            if inp['name'] == 'latent_image':
                inp['link'] = 170
                print(f"Updated Node 85 latent_image input to link 170")

# Remove the unload nodes
workflow['nodes'] = [n for n in workflow['nodes'] if n['id'] not in [clean_gpu['id'], clear_cache['id']]]
print(f"Removed nodes {clean_gpu['id']} and {clear_cache['id']}")

# Remove their links
workflow['links'] = [l for l in workflow['links'] if l[1] not in [clean_gpu['id'], clear_cache['id']] and l[3] not in [clean_gpu['id'], clear_cache['id']]]

# Save
with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, separators=(',', ':'))

print("\n[SUCCESS] Created workflow WITHOUT unload nodes:")
print("  user/default/workflows/video_wan2_2_14B_i2v_no_sage_test_NO_UNLOAD.json")
print("\nTest this and compare times!")



