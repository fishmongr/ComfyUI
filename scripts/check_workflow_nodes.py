import json

with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'r', encoding='utf-8') as f:
    w = json.load(f)

# Find existing nodes
existing = {n['id']: n['type'] for n in w['nodes']}
print("Existing high-ID nodes:")
for nid in sorted([i for i in existing.keys() if i >= 115]):
    print(f"  Node {nid}: {existing[nid]}")

# Check if cleanGpu nodes exist
has_clean = any('cleanGpu' in n['type'] for n in w['nodes'])
has_clear = any('clearCache' in n['type'] for n in w['nodes'])
print(f"\nHas cleanGpuUsed: {has_clean}")
print(f"Has clearCacheAll: {has_clear}")

# Check link 170 (from KSampler 86)
link_170 = [l for l in w['links'] if l[0] == 170]
if link_170:
    print(f"\nLink 170: from node {link_170[0][1]} to node {link_170[0][3]}")

