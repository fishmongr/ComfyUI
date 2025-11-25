import json

# Load OpenArt workflow
with open('user/default/workflows/openart_wan22_extracted.json', 'r', encoding='utf-8') as f:
    openart = json.load(f)

# Load your workflow
with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'r', encoding='utf-8') as f:
    yours = json.load(f)

print("=" * 60)
print("OPENART WORKFLOW MODEL LOADING")
print("=" * 60)

# Check WanVideoModelLoader nodes (they use custom wrapper)
loaders = [n for n in openart['nodes'] if 'ModelLoader' in n['type']]
print(f"\nModel loader nodes: {len(loaders)}\n")
for n in loaders:
    model_name = n['widgets_values'][0] if n.get('widgets_values') else 'N/A'
    mode = n.get('mode', 0)
    status = "ACTIVE" if mode == 0 else "BYPASSED"
    print(f"Node {n['id']} ({n['type']}): {status}")
    print(f"  Model: {model_name}")
    print(f"  Title: {n.get('title', 'N/A')}")
    
    # Check what it connects to
    outputs = [l for l in openart['links'] if l[1] == n['id']]
    if outputs:
        dest_ids = [l[3] for l in outputs]
        print(f"  Connects to nodes: {dest_ids}")
    print()

print("\n" + "=" * 60)
print("YOUR WORKFLOW MODEL LOADING")
print("=" * 60)

loaders = [n for n in yours['nodes'] if 'UNETLoader' in n['type']]
print(f"\nModel loader nodes: {len(loaders)}\n")
for n in loaders:
    model_name = n['widgets_values'][0] if n.get('widgets_values') else 'N/A'
    mode = n.get('mode', 0)
    status = "ACTIVE" if mode == 0 else "BYPASSED"
    print(f"Node {n['id']} ({n['type']}): {status}")
    print(f"  Model: {model_name}")
    
    # Check what it connects to
    outputs = [l for l in yours['links'] if l[1] == n['id']]
    if outputs:
        dest_ids = [l[3] for l in outputs]
        print(f"  Connects to nodes: {dest_ids}")
    print()

print("\n" + "=" * 60)
print("KEY DIFFERENCE")
print("=" * 60)
print("\nChecking if OpenArt uses sequential loading...")

# Check if samplers are connected in sequence
openart_samplers = [n for n in openart['nodes'] if 'Sampler' in n['type']]
print(f"\nOpenArt samplers: {len(openart_samplers)}")
for s in openart_samplers:
    print(f"  Node {s['id']}: {s.get('title', s['type'])}")



