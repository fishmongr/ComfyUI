import json

with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the unload nodes
clean_gpu = next((n for n in workflow['nodes'] if n['type'] == 'easy cleanGpuUsed'), None)
clear_cache = next((n for n in workflow['nodes'] if n['type'] == 'easy clearCacheAll'), None)

print("Unload nodes in workflow:")
print(f"  easy cleanGpuUsed: {'YES (Node {})'.format(clean_gpu['id']) if clean_gpu else 'NO'}")
print(f"  easy clearCacheAll: {'YES (Node {})'.format(clear_cache['id']) if clear_cache else 'NO'}")

if clean_gpu:
    print(f"\nNode {clean_gpu['id']} flow:")
    # Find what connects to it
    incoming = [l for l in workflow['links'] if l[3] == clean_gpu['id']]
    outgoing = [l for l in workflow['links'] if l[1] == clean_gpu['id']]
    
    if incoming:
        src = incoming[0]
        src_node = next((n for n in workflow['nodes'] if n['id'] == src[1]), None)
        print(f"  Input from: Node {src[1]} ({src_node['type'] if src_node else 'unknown'})")
    
    if outgoing:
        dest = outgoing[0]
        dest_node = next((n for n in workflow['nodes'] if n['id'] == dest[3]), None)
        print(f"  Output to: Node {dest[3]} ({dest_node['type'] if dest_node else 'unknown'})")

print("\n" + "="*60)
print("ANALYSIS")
print("="*60)

print("\nWhat the nodes DO:")
print("  - easy cleanGpuUsed: Calls torch.cuda.empty_cache() and soft_empty_cache()")
print("  - easy clearCacheAll: Clears ComfyUI's internal caches")

print("\nWhat they DON'T do:")
print("  - They don't unload model weights from VRAM")
print("  - They don't change model loading behavior")
print("  - ComfyUI already auto-manages model loading")

print("\nActual benefit:")
print("  - Clears cached tensors/activations between passes")
print("  - Might reduce memory fragmentation slightly")
print("  - Minimal performance impact (maybe 1-2s)")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("\nThe nodes are NOT harmful, but they're also NOT solving the offload issue.")
print("The 845MB offload is inherent to having both models loaded.")
print("\nOptions:")
print("  1. KEEP them - No harm, might help with memory fragmentation")
print("  2. REMOVE them - Simplify workflow, same performance")
print("  3. Test both - Run without them and compare times")



